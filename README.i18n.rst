

how to "translate" this webapp
===============================
 
how to run the steps necessary for the i18n process, where i18n means
 internationalization.

lingua 1.6
----------
* env/bin/python setup.py extract_messages    (each time, the code or templates change)
* env/bin/python setup.py init_catalog -l de  (only once, if you need a new language, e.g. 'de')
* env/bin/python setup.py update_catalog      (every time the POT changed)
* poedit c3spartyticketing/locale/de/LC_MESSAGES/c3sPartyTicketing.po  (to edit translations)
* env/bin/python setup.py compile_catalog     (manually turn PO into MO; poedit does this on save)
