.. _develop-test:

=======
Testing
=======
Part of the MultiProject quality control is testing. The project currently runs both :ref:`functional <test-func>` and
:ref:`performance <test-perf>` tests against the setups. To setup and run the tests, read the subsequent sections.

.. contents::
   :local:


.. _test-func:

Functional testing
==================

This document shortly describes how to get on going with the functional testing when doing the MultiProject
development. The functional testing runs the test cases using web browser against the existing MultiProject -setup.
Tests are written and run using Selenium based python wrapper, Splinter (http://splinter.cobrateam.info/)

.. contents::
   :local:

Preparations
------------
Following preparations are needed for running the functional tests.
Because of Windows limitations, specific steps are needed.

.. contents::
   :local:

Linux
~~~~~
In Linux environment:

- Setup MultiProject environment
- Install python modules::

    pip install splinter selenium nose

- Install Chrome driver

  - Download from http://code.google.com/p/chromium/downloads/list
  - Extract package and place ``chromedriver`` to path (eg. ``/usr/bin/chromedriver``)
  - Ensure that the user has the permissions to execute the chromedriver

Windows
~~~~~~~
In Windows environment:

If there are errors when installing splinter with pip, you can by-pass them as follows:

- Setup MultiProject environment
- Download chromedriver and put it inside the python/scripts folder
- Install selenium::

    pip install selenium

- Install ``lxml`` with ``pip`` (or with easy_install)::

    pip install lxml==2.3

- Clone git repo "git clone git://github.com/cobrateam/splinter.git" into some directory
- Checkout windows branch
- Change the line ``install_requires=['selenium==2.8.1', 'lxml==2.3.1'],`` from the setup.py
  to contain lxml==2.3 instead.
- In the folder containing the splinter's setup.py, run::

    python setup.py install

- Open terminal
- Make the PATH to include the python/scripts folder (remember, the chromedriver
  was put inside the python/scripts folder)
- Open the command line::

    C:\> O:
    O:\CQDE>cd tests\webtests\
    O:\CQDE\tests\webtests>nosetests cases\smoke.py

The following set of packages and versions worked:

- Fabric==1.3.4
- docutils==0.8.1
- funkload==1.16.1
- genshi==0.6
- lxml==2.3
- nose==1.1.2
- rdflib==3.1.0
- selenium==2.8.1
- splinter==0.4
- ssh==1.7.11
- trac==0.12.1
- webunit==1.3.10

Configure
---------
Use tests/webtests/tests.ini.sample as a template and create tests/webtests/tests.ini
to reflect the setup you're running the tests against:

- Create super user in service you're about to test (super user rights are needed for deleting the project
- Set the user name and password in ``tests.ini`` file accordingly

Running tests
-------------
Run the tests *in the webtests* folder, with command::

  cd tests/webtests
  nosetests cases/smoke.py

Writing tests
-------------
There are couple of things to keep in mind while writing/maintaining functional tests:

Navigate through links:
    When moving from view to another, prefer clicking the links instead of using direct URLs.
    This is because (at least in some cases), the authenticated session may be losed when using
    browser visit. Consider following example::

        browser = WebBrowser()
        browser.visit('http://locahost/myproject')
        project = ProjectLayout()
        project.navigation.admin.click()
        admin = AdminPage()
        admin.admin_navigation.system.click()
        # vs.
        browser.visit('http://locahost/myproject/admin/system')

Keep in same HTTP scheme:
    Use either HTTP or HTTPS, not both. Otherwise you'll get redirects, causing problems with functional tests and
    sessions. Thus, ensure you have following::

        # project.ini
        [multiproject]
        default_http_scheme = http

        # tests.ini
        [localhost]
        host = http://localhost/


.. _test-perf:

Performance testing
===================
This chapter describes how to prepare and execute performance tests against the MultiProject powered Trac -setup.
Performance tests are written on top of FunkLoad_, python based performance testing framework.

For running the tests, the service does not be running in same box. Actually, to avoid bending the results, the perf test
runner should be running in a different box.


.. contents::
   :local:

Preparations
------------
Before the tests can be run, setup the testing environment:

#. Install FunkLoad::

     pip install Funkload

#. Install command line apps::

     sudo apt-get install gnuplot


Configuration
-------------
By convention, the FunkLoad expects the find testing configuration file named after test case class. The needs to be
located in the folder where the test is run, or alternatively you point the configuration folder by defining environment
variable: :envvar:`FL_CONF_PATH`


#. Copy and edit the configuration based on needs::

     cp MultiprojectTestCase.example.conf MultiprojectTestCase.conf
     vim MultiprojectTestCase.conf

   Pay attention on following values:

   **accounts**:
        One or more accounts separated with comma. Each account is expected to be in format: username:password
        Example::

            [main]
            accounts=myuser:weoceecwe,anotheruser:wefoi32dve

        Test case will use them randomly when running the tests.

   **url**:
        URL where the service is running. Example::

            [main]
            url=https://localhost/

.. NOTE::

    Some of the parameters defined in configuration file and also be overwritten by passing parameters to
    FunkLoad runners.


Running
-------
Performance test case can be run in several ways, depending on the wanted outcome:

#. Run all the tests, as is (no concurrency etc.)::

    python perftests.py

#. Run performance bench::

    fl-run-bench -c 1:10:20 tests.py MultiprojectTestCase.test_smoke

   In this example, run three test cycles:

   - One user
   - Ten concurrent users
   - Twenty concurrent users

After successful execution, the report file (`*.xml`) is generated.

Reporting
---------
After running the performance tests, human readable report can be produced with commands:

#. In HTML format::

    fl-build-report -o report/html --html smoke-bench.xml

#. In ReST format::

    fl-build-report smoke-bench.xml > report.rst


Unit testing
============
Plugin comes with some unit tests, but unfortunately they have got outdated and would require
re-planning them anyway. Thus, when developing and testing, use :ref:`function testing <test-func>`


.. _FunkLoad: http://funkload.nuxeo.org/
