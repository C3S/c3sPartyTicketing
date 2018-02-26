How to "translate" this webapp
===============================
 
How to run the steps necessary for the i18n process, where i18n means internationalization.
For more about lingua, the Python translation toolset, see: https://pypi.python.org/pypi/lingua

lingua 1.6 (obsolete)
----------
* env/bin/python setup.py extract_messages    (each time, the code or templates changed)
* env/bin/python setup.py init_catalog -l de  (only once, if you need a new language, e.g. 'de')
* env/bin/python setup.py update_catalog      (every time the POT changed)
* poedit c3spartyticketing/locale/de/LC_MESSAGES/c3sPartyTicketing.po  (to edit translations)
* env/bin/python setup.py compile_catalog     (manually turn PO into MO; poedit does this on save)

lingua 2.3 (and later)
----------
* installation 
    * gettext: sudo apt-get install gettext
* only once, if you need a new language, e.g. 'de'
    * mkdir -p c3spartyticketing/locale/de/LC_MESSAGES
    * msginit -l de -o c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.po

* each time the code or templates changed, (re)create the .pot file:
    * env/bin/pot-create -o c3spartyticketing/locale/c3spartyticketing.pot c3spartyticketing
* every time the .pot file changed, (re)create the po file(s)
    for german:
    * msgmerge --update c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.po c3spartyticketing/locale/c3spartyticketing.pot
    for all languages:
    * msgmerge --update c3spartyticketing/locale/*/LC_MESSAGES/c3spartyticketing.po c3spartyticketing/locale/c3spartyticketing.pot

* to edit translations edit the .po file with poedit:
    * poedit c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.po
* every time the .po file changed, create a .mo file
    * msgfmt -o c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.mo c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.po
