 c3sPartyTicketing README
==========================

Getting Started
---------------

- git clone git@github.com:C3S/c3sPartyTicketing.git 
- cd c3sPartyTicketing

- git branch -a # show branches to checkout the latest one, e.g.:
- git checkout -b C3Sevents_2017_01_GvBc --track origin/C3Sevents_2017_01_GvBc

- git branch C3Sevents_2018_01_GvBc # create your new branch
- git checkout C3Sevents_2018_01_GvBc

- pip install virtualenv # setup own python environment
- virtualenv env

- env/bin/python setup.py develop
- env/bin/initialize_c3sPartyTicketing_db development.ini # initialize database
- env/bin/pserve development.ini # run web service

Translations
------------

After changes of texts in code or templates:
-> env/bin/pot-create -o c3spartyticketing/locale/c3spartyticketing.pot c3spartyticketing

Every time the .pot file changed, recreate the .po files for all languages
-> msgmerge --update c3spartyticketing/locale/*/LC_MESSAGES/c3spartyticketing.po c3spartyticketing/locale/c3spartyticketing.pot

To edit translations, change the .po file via poedit
-> poedit c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.po

Every time the .po file changed, create a .mo file
-> msgfmt -o c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.mo c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.po