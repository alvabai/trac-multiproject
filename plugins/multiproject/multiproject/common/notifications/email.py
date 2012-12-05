# -*- coding: utf-8 -*-
import os
import time
import socket
import smtplib
from genshi.template.text import TextTemplate, NewTextTemplate
import pkg_resources

from trac.core import Component, implements, TracError
from trac.admin import IAdminCommandProvider, AdminCommandError
from trac.notification import NotifyEmail
from trac.util.text import printout
from trac.util.translation import _
from trac.web.chrome import ITemplateProvider, Chrome

from multiproject.common.env import MultiProjectEnvironmentInit
from multiproject.common.projects import Project, HomeProject


class EmailNotifier(NotifyEmail):
    """
    Send email notification using SMTP service defined
    By default uses the plain ``notify.txt`` template with only variable::

        ${body}

    Example usage::

        # Simple
        enotify = EmailNotifier(conf.home_env, "Subject", "Body")
        enotify.notify('foo.bar@company.com')

        # Advanced
        enotify = EmailNotifier(conf.home_env, 'Subject', {'placeholder:'Value'})
        enotify.template_name = 'custom.txt'
        enotify.notify_user(project, user)

    """
    template_name = "notify.txt"

    def __init__(self, env, subject=None, data=None):
        NotifyEmail.__init__(self, env)
        self.to = []
        self.cc = []
        self.from_email = env.config.get('notification', 'smtp_from')
        self.subject = subject or ''
        # If string given, place it into body variable, otherwise use dict or empty dict
        self.data = {'body':data} if isinstance(data, basestring) else data or {}

    def notify_admins(self, project):
        self.to = project.get_admin_email_addresses()
        self.notify(self.to)

    def notify_system_admins(self, project):
        if not isinstance(project, HomeProject):
            emails = HomeProject().get_admin_email_addresses()
        else:
            emails = project.get_admin_email_addresses()
        self.notify(emails)

    def notify_members(self, project):
        self.to = project.get_team_email_addresses()
        self.notify(self.to)

    def notify_author(self, project):
        self.to = project.author.mail
        self.notify(self.to)

    def notify_user(self, project, user):
        self.to = project.get_email_addess(user)
        self.notify(self.to)

    def notify_emails(self, emails):
        self.to = emails
        self.notify(self.to)

    def notify(self, to, cc=None, subject=None, body=None):
        """
        Provide a direct way to send an email

        :param list to: Email addresses where to send email to
        :param list cc: CC email addresses
        :param str subject: Email subject if not set in init (or want to override it)
        :param str subject: Email body if not set in init (or want to override it)
        :raises: TracError if email sending fails
        """
        self.to = [to] if isinstance(to, basestring) else to
        self.cc = cc or []
        self.subject = subject or self.subject

        # If body msg is set, use it as-is
        if body:
            self.data = {'body':body}
            self.template = NewTextTemplate('${body}')

        # Load non-default template
        elif self.template_name != 'notify.txt':
            # Reload template so that it can be set after for the instance
            self.template = Chrome(self.env).load_template(self.template_name, method='text')

        # Raise possible exceptions (connection, smtp) as unified TracError
        try:
            return super(EmailNotifier, self).notify(None, self.subject)
        except (socket.error, smtplib.SMTPException), e:
            self.env.log.exception('Failed to send email to: %s' % self.to)
            raise TracError(e)

    def get_recipients(self, resid):
        return self.to, self.cc


class NotifyTemplateProvider(Component):
    implements(ITemplateProvider)

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('multiproject.common.notifications', 'templates')]

    def get_htdocs_dirs(self):
        return [('multiproject', pkg_resources.resource_filename(__name__, 'htdocs'))]


class NotificationCommandProvider(Component):
    """
    Class implements trac-admin commands related to home project functionality
    """

    implements(IAdminCommandProvider)

    # IAdminCommandProvider methods

    def get_admin_commands(self):
        yield ('mp user notify', '<str:permission> <str:email-template-file> [debug-only]',
               """Sends a notification email to the admins.

               The first line of the template is expected to be the subject.
               The template can contain string ${env_name}, which is replaced by the project name.

               If optional debug flag. If value is "true", command only prints what would be sent,
               but does not actually send emails.
               """,
               None, self._notify_admins)

    def _notify_admins(self, permission, email_path, debug='false'):
        is_debug = debug.lower() in ('true', 'yes')

        if permission != 'TRAC_ADMIN':
            raise AdminCommandError('Only TRAC_ADMIN permission is supported')

        # A standard thing to do in IAdminCommandProviders (otherwise,
        # accessing project_identifier would give errors)
        if not hasattr(self.env, 'project_identifier'):
            MultiProjectEnvironmentInit(self.env).environment_needs_upgrade(None)

        env_name = self.env.project_identifier
        if env_name == self.env.config.get('multiproject', 'sys_home_project_name'):
            raise AdminCommandError('Command does not support home project')

        if not os.path.exists(email_path):
            raise AdminCommandError(_("Email template was not found!"))

        project = Project.get(env_name=self.env.project_identifier)
        email_template = ''
        try:
            with open(email_path) as fd:
                email_template = fd.read()
        except OSError as e:
            raise AdminCommandError(_("Error with opening file %(path)s: %(error_msg)s",
                path=email_path, error_msg=e))
        except Exception as e:
            raise AdminCommandError(_("Unknown error when parsing file %(path)s: %(error_msg)s",
                path=email_path, error_msg=e))
        email_template = [i.strip() for i in email_template.split('\n', 1) if i]
        if not len(email_template) > 1 or not all(email_template):
            raise AdminCommandError(_("Email template %(path)s was invalid.", path=email_path))

        subject, body = email_template
        text_template = NewTextTemplate(body)
        admins = project.get_admin_email_addresses()

        data = {'env_name': env_name}

        if is_debug:
            printout('## DEBUG MODE - NOT SENDING EMAILS ##')

        printout("project: {0}".format(env_name))
        printout("to: {0}".format(','.join(admins)))
        printout("subject: {0}".format(subject))
        printout("----------------------------")
        printout(text_template.generate(**data))
        printout("----------------------------")

        if not is_debug:
            notifier = EmailNotifier(self.env, subject=subject, data=data)
            notifier.template = text_template
            notifier.notify(admins)
            printout('Emails sent')
