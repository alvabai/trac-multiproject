# -*- coding: utf-8 -*-
import socket
import smtplib
from genshi.template.text import TextTemplate, NewTextTemplate
from pkg_resources import resource_filename

from trac.core import Component, implements, TracError
from trac.notification import NotifyEmail
from trac.web.chrome import ITemplateProvider, Chrome


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
        self.to = project.get_admin_email_addesses()
        self.notify(self.to)

    def notify_system_admins(self, project):
        self.to = project.get_system_admin_email_addesses()
        self.notify(self.to)

    def notify_members(self, project):
        self.to = project.get_team_email_addesses()
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
        else:
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
        return [resource_filename('multiproject.common.notifications', 'templates')]

    def get_htdocs_dirs(self):
        return []
