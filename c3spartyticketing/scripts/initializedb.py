# -*- coding: utf-8  -*-
import os
import sys
import transaction
from datetime import datetime
from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    PartyTicket,
    C3sStaff,
    Group,
    Base,
)


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    # a group for accountants/staff
    with transaction.manager:
        accountants_group = Group(name=u"staff")
        try:
            DBSession.add(accountants_group)
            DBSession.flush()
            print("adding group staff")
        except:
            print("could not add group staff.")
            # pass
    with transaction.manager:
        # staff personnel
        staffer1 = C3sStaff(
            login=u"rut",
            password=u"berries",
            email=u"noreply@c3s.cc",
        )
        staffer1.groups = [accountants_group]
        try:
            DBSession.add(staffer1)
            print("adding staff rut")
            DBSession.flush()
        except:
            print("it borked! (rut)")
            # pass
    # one more staffer
    with transaction.manager:
        staffer2 = C3sStaff(
            login=u"reel",
            password=u"boo",
            email=u"noreply@c3s.cc",
        )
        staffer2.groups = [accountants_group]
        try:
            DBSession.add(staffer2)
            print("adding staff reel")
            DBSession.flush()
        except:
            print("it borked! (reel)")
            # pass
    # a ticket, actually a ticket form submission
    with transaction.manager:
        ticket = PartyTicket(
            firstname=u'Färst',
            lastname=u'Läst',
            email=u"foo@shri.de",
            password=u"berries",
            locale=u"DE",
            email_is_confirmed=False,
            email_confirm_code=u"ABCDEFGHIJ",
            num_tickets=u'10',
            ticket_type=2,
            the_total=150,
            date_of_submission=datetime.now(),
            #num_foodstamps=10,
            user_comment=u'no comment.'
        )
        try:
            DBSession.add(ticket)
            print("adding Firstnäme")
        except:
            pass
