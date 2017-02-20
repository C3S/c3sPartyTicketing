import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'alembic',
    'Babel',
    'Chameleon==2.22',
    'cryptacular',
    'deform',
    'gnupg',
    'python-gnupg',
    #'lingua==1.6',
    'lingua',
    'Pillow==2.4.0',  # fork of PIL; needed for qrcode
    'pyramid==1.6',
    'pyramid_beaker',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_mailer==0.14',
    'pyramid_tm==0.11',
    'python-dateutil',
    'qrcode',
    'repoze.sendmail<4.2',  # pin down, see
    # https://github.com/repoze/repoze.sendmail/issues/31+    
    'raven',
    'requests',
    'SQLAlchemy==1.0.9',
    'transaction==1.4.3',
    'unicodecsv',
    'waitress',
    'zope.sqlalchemy',
    'PasteDeploy'
]
test_requires = [
    'nose',
    'coverage',
    'webtest',
    'selenium',
]
docs_require = [
    'sphinx',  # for generating the documentation
    'sphinxcontrib-plantuml',
]
setup(
    name='c3sPartyTicketing',
    version='0.0',
    description='c3sPartyTicketing',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='c3spartyticketing',
    install_requires=requires + test_requires + docs_require,
    entry_points="""\
      [paste.app_factory]
      main = c3spartyticketing:main
      [console_scripts]
      initialize_c3sPartyTicketing_db = c3spartyticketing.scripts.initializedb:main
      """,
    message_extractors={
        'c3spartyticketing': [
            ('**.py', 'lingua_python', None),
            ('**.pt', 'lingua_xml', None),
        ]},
)
