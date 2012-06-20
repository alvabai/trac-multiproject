from setuptools import find_packages, setup

import multiproject


# name can be any name.  This name will be used to create .egg file.
# name that is used in packages is the one that is used in the trac.ini file.
# use package name as entry_points
setup(
    name='TracMultiProject',
    version=multiproject.__version__,
    description='Trac Multiproject plugin - Create and host multiple projects on Trac',
    long_description=open('README.txt').read(),
    author='Nokia',
    author_email='nokia.developer.projects@nokia.com',
    url='http://projects.developer.nokia.com/multiproject',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Trac',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: JavaScript',
        'Operating System :: POSIX :: Linux'
    ],
    packages=find_packages(exclude = ['*.tests*']),
    zip_safe=False,
    entry_points="""
        [trac.plugins]
        multiproject = multiproject
        multiproject.common = multiproject.common
        multiproject.project = multiproject.project
        multiproject.home = multiproject.home
    """,
    package_data={
        'multiproject.common.web': ['htdocs/css/*.css', 'htdocs/js/*.js', 'htdocs/images/*.*'],
        'multiproject.common.membership': ['templates/*.txt'],
        'multiproject.common.admin': ['templates/*.html'],
        'multiproject.common.users': ['templates/*.html', 'templates/*.txt', 'htdocs/js/*.js'],
        'multiproject.common.notifications': ['templates/*.txt'],
        'multiproject.common.pagination': ['templates/*.html'],
        'multiproject.common.wiki': ['templates/*.html'],
        'multiproject.home.admin': ['templates/*.html','templates/*.txt', 'htdocs/js/*.js', 'htdocs/css/*.css'],
        'multiproject.home.frontpage': ['templates/*.html'],
        'multiproject.home.projectlist': ['templates/*.html', 'templates/*.rss'],
        'multiproject.home.rss': ['templates/*.*'],
        'multiproject.home.watchlist': ['templates/*.html', 'templates/*.rss'],
        'multiproject.home.timeline': ['templates/*.html', 'templates/*.rss'],
        'multiproject.project.summary': ['templates/*.html', 'htdocs/js/*.js', 'htdocs/css/*.css'],
        'multiproject.project.news': ['templates/*.html'],
        'multiproject.project.membership': ['templates/*.html'],
        'multiproject.project.admin': ['templates/*.html', 'htdocs/js/*.js', 'htdocs/css/*.css'],
        'multiproject.project.files': ['templates/*.html'],
        'multiproject.project.ticket': ['templates/*.html']
    },
    install_requires=[
        'Trac >= 0.12.1, < 0.13',
        'SQLAlchemy >= 0.6beta1, < 0.8',
        'TracXMLRPC',
        'python-memcached >= 1.43',
        'python-ldap >= 2.3.10',
        'PIL',
        'MySQL-python >= 1.2.2'
    ],
    extras_require={
        'mercurial': ['mercurial >= 1.7.5', 'TracMercurial >= 0.12.0'],
        'git': ['TracGit >= 0.12.0'],
        'mastertickets': ['TracMasterTickets >= 3.0'],
        'batchmodify': ['BatchModify >= 0.8.0'],
        'downloads': ['TracDownloads >= 0.3'],
        'discussion': ['TracDiscussion >= 0.8'],
        'wysiwyg': ['TracWysiwyg >= 0.12.0']
    },
    test_suite='multiproject.tests.alltests.suite'
)
