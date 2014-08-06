

how to "translate" this webapp
===============================
 
how to run the steps necessary for the i18n process, where i18n means
 internationalization.

lingua 1.6
----------
* env/bin/python setup.py extract_messages    (each time, the code or templates changed)
* env/bin/python setup.py init_catalog -l de  (only once, if you need a new language, e.g. 'de')
* env/bin/python setup.py update_catalog      (every time the POT changed)
* poedit c3spartyticketing/locale/de/LC_MESSAGES/c3sPartyTicketing.po  (to edit translations)
* env/bin/python setup.py compile_catalog     (manually turn PO into MO; poedit does this on save)

lingua 2.3
----------
* installation 
    * gettext: sudo apt-get install gettext
* only once, if you need a new language, e.g. 'de'
    * mkdir -p c3spartyticketing/locale/de/LC_MESSAGES
    * msginit -l de -o c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.po
* each time, the code or templates changed, creates a POT:
    * env/bin/pot-create -o c3spartyticketing/locale/c3spartyticketing.pot c3spartyticketing
* every time the POT changed, creates a PO
    * msgmerge --update c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.po c3spartyticketing/locale/c3spartyticketing.pot
* to edit translations
    * poedit c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.po
* every time the PO changed, creates a MO
    * msgfmt -o c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.mo c3spartyticketing/locale/de/LC_MESSAGES/c3spartyticketing.po