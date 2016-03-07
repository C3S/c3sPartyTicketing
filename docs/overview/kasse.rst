.. _overview_kasse:


Wie funktioniert die Kasse?
===========================


0) eingrooven
1) anmelden
2) tickets einlesen
2a) qr-codes
2b) alphanum. codes
3) Einchecken/Nachzahlen
3a) Nachzahlen
3b) Einchecken
3c) Abendkasse ohne Vorverkauf


0) eingrooven
--------------
ticke-ting, ticke-tick-tick ting!
ticke-ting, ticke-tick-tick ting!
ticke-ting, ticke-tick-tick ting!
bumm ba-ba-ba bumm!
(REPEAT)


1) (authentifizieren)
---------------------
Kassenpersonal muss sich am besten vorab am ticketingsystem ausweisen:

  https://events.c3s.cc/k  (login für die kasse)

username und passwort gibts bei christoph.


2) tickets checken
------------------
Wenn jemand mit einem Ticket erscheint, so ist das entweder

* ein QR-Code (ausgedruckt oder auf mobilem Endgerät) oder
* ein alphanumerischer Code (bspw. ABCDEFGHI123)


2a) (QR-Code)
-------------

Die QR-codes können einfach gescannt werden. sie enthalten eine URL, die
aufgerufen werden muss.
Das aufrufen dieser URL funktioniert nur, wenn man an der kasse
angemeldet und somit authorisiert ist, siehe (1)


2b) (Alphanumerischer Code)
---------------------------

Der Code kann auch von Hand eingegeben werden. dafür gibt es im
Kassensystem eine Maske:

  http://0.0.0.0:6545/k  bzw.  http://0.0.0.0:6545/kasse

(erstere URL leitet -- wenn angemeldet -- auf zweitere weiter, sodass
man sich nur die erste merken muss.)

es reicht die eingabe der ersten zeichen, um eine liste der passenden
codes zu bekommen.
der richtige muss angewählt werden. dann GO! klicken.


3) Einchecken / Nachzahlen / Abendkasse
----------------------------------------

Die folgende Seite zeigt an,

 * ob das Ticket bezahlt wurde (grüne vs rote ampel)
   - falls nicht, wie viel zu zahlen ist
 * wie viele Personen mit dem Ticket reisen können.
 * wie viele schon eingecheckt sind auf dem Ticket.


3a) Nachzahlen
---------------

Falls das Ticket nicht bezahlt und die Überweisung nicht bestätigt
wurde, kommt die rote Ampel und ein Hinweis, dass noch zu zahlen ist
("Zahlen, bitte!"), nebst der Summe (offener Betrag). Nach Einnahme der
Summe kann "Hat bezahlt" angeklickt werden.


3b) Einchecken
---------------

Falls schon bezahlt wurde, sieht man die Ticketdaten: Code, Fahrscheine,
"an Bord", Tickettyp.

Es muss die Anzahl an Personen eingegeben werden, die aktuell zusteigt.
Voreinstellung ist eine Person pro Check-In. Es können mehrere bis zur
offenen Anzahl eingecheckt werden.
Dabei bleiben evtl noch freie Fahrscheine übrig.
Beispiel: jemand hat ein Ticket für 10 Personen, es stehen aber nur 5 am
Eingang. Dann bitte "5" auswählen und "Check in!" anklicken.


3c) Abendkasse ohne Vorbestellung
----------------------------------

Personen, die nicht vorbestellt haben, können ad hoc ein Ticket
nachlösen. Dafür gibt es unter /kasse die Option "Neues Ticket".
Genauer: unter "/new_ticket" kann man auswählen, wie viele Personen ein
Ticket welcher Kategorie bekommen. Das Geld muss natürlich eingezogen
werden.


WICHTIG
========

Die eingeckeckten Personen müssen einen Stempel bekommen, damit klar
ist, das sie "rein" dürfen.
Es gibt zwei Arten Stempel:

* einfach (nur Party & Konzert unten)
* mit Speisewagen (mit Bürozugang/Essensmarke)
