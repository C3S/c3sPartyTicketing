.. _sec_templates:

=========
Templates
=========


Overview of templates used
==========================

The main event ticketing views are those for members and nonmembers.
The relevant views use templates
to render and display information to the users.

Tickets for Members
-------------------



* end.pt
* party.pt
* confirm.pt
* success.pt

.. figure::
   :caption: Views and templates for member users.
.. uml::

   @startuml
   start
   if (registration end reached?) then (yes)
     :Tell member registration has ended
     **end.pt**;
   else (no)
     :Nonmember creates ticket
     **party.pt**;
     :Nonmember reviews and confirms information
     **confirm.pt**;
     :Nonmember success page
     **success.pt**;
   endif
   stop
   @enduml

Tickets for Non-Members
-----------------------

* nonmember_end.pt
* nonmember.pt
* nonmember_confirm.pt
* nonmember_success.pt

.. figure::
   :caption: Views and templates for non-member users.
.. uml::

   @startuml
   start
   if (registration end reached?) then (yes)
     :Tell people registration has ended
     **nonmember_end.pt**;
   else (no)
     :Nonmember creates ticket
     **nonmember.pt**;
     :Nonmember reviews and confirms information
     **nonmember_confirm.pt**;
     :Nonmember success page
     **nonmember_success.pt**;
   endif
   stop
   @enduml


Location and venue information
------------------------------

The form and success views feature information
about the venue and relevant places.

As this information is reused in several places in the templates,
includable template snpiiets have been built for the venues.

* location.hpz.pt
* location.c3shq.pt
* location.freiland.pt

Likewise, information about both BarCamp and general assembly
are reused in several places:

* barcamp.hpz.pt
* assembly.c3shq.pt
