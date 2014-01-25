The app uses deform to build the main form
(and colander to create the application datastructure aka appstruct).

The form and the other pages (templates) are fully i18n'ized. To make deform
play nicely (like show localized error messages for form items), you can copy
deform's .po and .mo files to your locale folder(s) like so::

   cp env/lib/python2.7/site-packages/deform-<VERSION>-py2.7.egg/deform/locale/de/LC_MESSAGES/deform.* c3spartyticketing/locale/de/LC_MESSAGES/

The two files in this folder help show a slider widget, see ../README.Slider.rst
