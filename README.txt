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

- env/bin/python setup.py develop # only once

- rm c3sPartyTicketing.sqlite # if one existed before
- env/bin/initialize_c3sPartyTicketing_db development.ini # initialize database -- also needs to be done, if database layout has changed (models.py) or initialization code was changed

- env/bin/pserve development.ini # run web service


Translations
------------

 see README.i18n.rst

