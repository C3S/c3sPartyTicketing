The Slider in the membership application form is built with jquery.

You need to patch your local deform widgets.py
and add a slider named `selectslider.pt`.

To widgets.py add a class **SelectSliderWidget** similar to
**SelectWidget** like so::

  class SelectSliderWidget(Widget):
  """
  renders a slider widget using jquery
  """
  template = 'selectslider'


Depending on your setup, you find the files under::

   env/lib/python2.7/site-packages/deform-VERSION-py2.7.egg/deform/widget.py


The template can be put under 'deform/templates/selectslider.pt'
and it could look like the file in this folder.
