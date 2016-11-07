c3sPartyTicketing README
==========================

Getting Started
---------------

- git clone git@github.com:C3S/c3sPartyTicketing.git 
- cd c3sPartyTicketing

- git branch # show branches to checkout the latest one, e.g.:
- git checkout -b C3Sevents_2017_01_GvBc --track origin/C3Sevents_2017_01_GvBc

- pip install virtualenv
- virtualenv env

- env/bin/python setup.py develop
- env/bin/initialize_c3sPartyTicketing_db development.ini # initialize database
- env/bin/pserve development.ini # run web service

