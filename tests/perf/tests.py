# -*- coding: utf-8 -*-
"""
Module contains the performance tests cases, written using python based performance testing framework:
Funkload (http://funkload.nuxeo.org/)

See docs/test/perf.rst for instructions how to setup and run the performance tests.
"""
import urlparse
import os
import unittest
from random import choice

from funkload.FunkLoadTestCase import FunkLoadTestCase

class MultiprojectTestCase(FunkLoadTestCase):
    """
    This test case uses the configuration file: MultiprojectTestCase.conf
    """
    def setUp(self):
        #self.debugHeaders()
        self._form_token = ''
        self._accept_invalid_links = True
        self.server_url = self.conf_get('main', 'url')
        self.login_url = self._join_path(project='home', path='user')

    def authenticate(self, username, password):
        """
        Authenticate to service with given username and password.

        .. NOTE:: This imitates the normal web form

        """
        # Do first get request to login page so that we get the form token from cookie
        response = self.go(path=self.login_url)
        rcookies = self.get_used_cookies(response)

        # Construct and send post
        params = {
            'username':username,
            'password':password,
            '__FORM_TOKEN':rcookies['trac_form_token'],
            'action':'do_login'
        }
        self.logi('Authenticating with account: %s' % username)
        response = self.post(self.login_url, params, load_auto_links=False)

        #self.logi('Response cookies: %s' % response.cookies)
        return response


    def go(self, project='home', path='/', **kwargs):
        """
        Convenience function to do get requests using paths only.

        :param str project: Name of the project, defaults to 'home'
        :param str path: URL path, joined with the server url and project
        :params kwargs: Additional parameters to pass to Funkload's get request
        """
        url = self._join_path(project, path)

        self.logdd('>>>>>>>>>>>>> before request %s' % url)
        response = self.get(url, description=url, **kwargs)
        self.logdd('<<<<<<<<<<<<< after request')

        return response

    def get_random_account(self):
        """
        Return random account as a dictionary from the configured accounts

        >>> self.get_random_account()
        >>> {'username':'myaccount', 'password':'sdfwefkonwdwwer'}

        :returns: Random account info
        """
        keys = ['username', 'password']
        account = choice(self.conf_getList(section='main', key='accounts', separator=','))

        if ':' not in account:
            raise Exception('Account value is invalid, excepting format: username:password')

        # Return dictionary: {'username':'myaccount', 'password':'sdfwefkonwdwwer'}
        return dict(zip(keys, (account.split(':'))))

    def get_random_project(self):
        """
        Returns random project as a dictionary from the configured accounts

        >>> self.get_random_project()
        >>> {'name':'projectname', 'url':'https://mysetup.com/projectname'}

        :returns: Random project info in a dict
        """
        project_names = self.conf_getList(section='main', key='projects', default='', separator=',')

        if not project_names:
            return {}

        project_name = choice(project_names)
        return {'name':project_name, 'url':self._join_path(project=project_name)}


    def get_used_cookies(self, response):
        """
        Returns the dictionary of the used cookies from the given
        response.

        The implementation is adapted from webunit.webunitests.py

        :returns: Cookies in dictionary. Example: {'trac_form_token':'23abde422bcfa342adefa'}
        """
        used_cookies = {}

        for domain, cookies in response.cookies.items():
            # Check cookie domain
            if not response.server.endswith(domain):
                continue
            for path, cookies in cookies.items():
                # Check that the path matches
                urlpath = urlparse.urlparse(response.url)[2]
                if not urlpath.startswith(path) and not (path == '/' and urlpath == ''):
                    continue
                for sendcookie in cookies.values():
                    # Check the cookie is or isn't secure
                    if sendcookie['secure'] and response.protocol != 'https':
                        continue
                    used_cookies.update({sendcookie.key:sendcookie.coded_value})

        return used_cookies


    def _join_path(self, project, path='/'):
        """
        Joins given path with service URL and returns in back
        """
        path = path[1:] if path.startswith('/') else path
        url = path if path.startswith('http') else os.path.join(self.server_url, project, path)

        return url


    def test_smoke(self):
        """
        Go through most of the service views
        """
        account = self.get_random_account()
        project = self.get_random_project()

        self.authenticate(account['username'], account['password'])
        self.go('home', 'myprojects')
        self.go('home', 'globaltimeline')

        if not project:
            self.logi('No project(s) defined, cannot continue from here')
            return

        pname = project['name']
        self.go(pname)
        self.go(pname, 'wiki')
        self.go(pname, 'timeline')
        self.go(pname, 'roadmap')
        self.go(pname, 'browser')
        self.go(pname, 'files')
        self.go(pname, 'query')
        self.go(pname, 'search')
        self.go(pname, 'discussion')



if __name__ in ('main', '__main__'):
    unittest.main()


