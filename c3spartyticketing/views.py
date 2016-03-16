# -*- coding: utf-8 -*-
"""
This module holds utility functions for the main ticket forms.


**C3S Members**
  have received an invitation email with a link (containing a **token**).
  This link triggers c3sPartyTicketing to ask relevant information
  via REST-API call from c3sMembership, so first and last name
  as well as membership type are known to c3sPartyTicketing.

**Nonmembers**
  who go to the ticketing site
  are presented with the non-member form.

"""
from datetime import datetime
import dateutil.parser
import deform
from pkg_resources import resource_filename

from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import (
    TranslationStringFactory,
    get_localizer,
)
from pyramid.threadlocal import get_current_request

from c3spartyticketing.models import PartyTicket


_ = TranslationStringFactory('c3spartyticketing')


def translator(term):
    return get_localizer(get_current_request()).translate(term)

my_template_dir = resource_filename('c3spartyticketing', 'templates/')
deform_template_dir = resource_filename('deform', 'templates/')
zpt_renderer = deform.ZPTRendererFactory(
    [
        my_template_dir,
        deform_template_dir,
    ],
    translator=translator,
)


def ticket_appstruct(request, view=''):
    """
        Ensures the consistent creation of a valid ticket appstruct.
        Tries creation in the following order:

        1. Use from possibly edited session (reedit, refresh)
        2. If id not given, create new from userdata
        3. If id given, create from dbenty
        4. Redirect to access denied url
    """
    print('--- creating appstruct ------------------------------------------')

    userdata = request.session['userdata']
    assert(userdata)
    print "userdata: {}".format(userdata)

    if 'appstruct' in request.session:
        # Use from possibly edited session (reedit, refresh).
        print('using session:')
        appstruct = request.session['appstruct']
        if appstruct is None:
            return HTTPFound(
                location=request.registry.settings[
                    'registration.access_denied_url'
                ]
            )
        print "-- appstruct: {}".format(appstruct)
        return appstruct

    userdata = request.session['userdata']
    if userdata['id'] is 'None':
        # If id not given, create new from userdata
        print("using userdata for new form.")
        appstruct = {
            'ticket': request.session['userdata']
        }
        print "-- appstruct: {}".format(appstruct)
        return appstruct

    # Create from dbenty
    assert(userdata['id'])
    _ticket = PartyTicket.get_by_id(userdata['id'])
    assert isinstance(_ticket, PartyTicket)
    print "using dbentry (id {}):".format(userdata['id'])
    appstruct = {
        'ticket': {
            'ticket_gv': _ticket.ticket_gv_attendance,
            'ticket_bc': [
                'attendance',
                'buffet'
            ],
            # 'ticket_all': _ticket.ticket_all,
            'ticket_all': False,
            'ticket_support': [
                '1',
                '2',
                '3',
                '4',
            ],
            'support': _ticket.support,
            'the_total': _ticket.the_total,
            'comment': _ticket.user_comment,
            'ticket_tshirt': _ticket.ticket_tshirt,
            'firstname': _ticket.firstname,
            'lastname': _ticket.lastname,
            'token': _ticket.token,
            'email': _ticket.email,
            '_LOCALE_': _ticket.locale
        },
        'representation': {
            'firstname': _ticket.rep_firstname,
            'lastname': _ticket.rep_lastname,
            'email': _ticket.rep_email,
            'street': _ticket.rep_street,
            'zip': _ticket.rep_zip,
            'city': _ticket.rep_city,
            'country': _ticket.rep_country,
            'representation_type': _ticket.rep_type
        },
        # 'tshirt': {
        #    'tshirt_type': _ticket.ticket_tshirt_type,
        #    'tshirt_size': _ticket.ticket_tshirt_size
        # }
    }
    if not _ticket.ticket_bc_attendance:
        appstruct['ticket']['ticket_bc'].remove('attendance')
    if not _ticket.ticket_bc_buffet:
        appstruct['ticket']['ticket_bc'].remove('buffet')
    if not _ticket.ticket_support:
        appstruct['ticket']['ticket_support'].remove('1')
    if not _ticket.ticket_support_l:
        appstruct['ticket']['ticket_support'].remove('2')
    if not _ticket.ticket_support_xl:
        appstruct['ticket']['ticket_support'].remove('3')
    if not _ticket.ticket_support_xxl:
        appstruct['ticket']['ticket_support'].remove('4')

    print "-- appstruct: {}".format(appstruct)
    return appstruct


def check_route(request, view=''):
    """
    Decides, based on ...

        A. This function performs checks:
            1.  *userdata* check:
                *userdata* has to be set in *load_user*.
                *load_user()* is the only entrance door.
                If *userdata* is not set,
                redirect to access denied url

            3.  dbentry check:
                If *finish_on_submit* is active and user has already submitted,
                redirect to finished view

            4.  date check:
                If registration period is over,
                redirect to finished view

        B. individual routes:
            redirects based on keywords in POST
    """
    print('--- pick route --------------------------------------------------')
    if view:
        print('called from view: %s') % view

    # ## checks

    # userdata check:
    if 'userdata' in request.session:
        userdata = request.session['userdata']
        try:
            assert('token' in userdata)
            assert('id' in userdata)
            assert('firstname' in userdata)
            assert('lastname' in userdata)
            assert('email' in userdata)
            assert('mtype' in userdata)
        except:
            print('userdata test: user not found. redirecting...')
            return HTTPFound(
                location=request.registry.settings[
                    'registration.access_denied_url']
            )
    else:
        print('userdata test: user not found. redirecting...')
        return HTTPFound(
            location=request.registry.settings[
                'registration.access_denied_url']
        )

    # dbentry check:
    if view is not 'finished' and view is not 'confirm':
        if 'true' in request.registry.settings[
                'registration.finish_on_submit']:
            if PartyTicket.has_token(userdata['token']):
                print('dbentry check: ticket already exists. redirecting...')
                return HTTPFound(location=request.route_url('finished'))
            else:
                print('token check: ticket does not exist')
        else:
            print('token check: deactivated')

    # date check:
    if view is not 'finished':
        today = datetime.today().date()
        registration_endgvonly = dateutil.parser.parse(
            request.registry.settings['registration.endgvonly']
        ).date()
        if today > registration_endgvonly:
            print('date check: registration is finished. redirecting ...')
            # if ticket was already submitted, show finished ticket
            if PartyTicket.has_token(userdata['token']):
                return HTTPFound(location=request.route_url('finished'))
            # else show userfeedback: registration has ended
            return HTTPFound(location=request.route_url('end'))
        else:
            print('date check: registration is still possible')

    # ## individual routes

    # confirm view:
    if view is 'confirm':

        if 'appstruct' not in request.session:
            return HTTPFound(location=request.route_url('party'))

        # reedit: user wants to re-edit her data
        if 'reedit' in request.POST:
            return HTTPFound(location=request.route_url('party')+'?reedit')

        # order: user wants to confirm the data
        if 'confirm' in request.POST:
            return

        # order: user confirmed the data
        if 'confirmed' in request.POST:
            request.session['flags'] = {
                'confirmed': True
            }
            return HTTPFound(location=request.route_url('success'))

    # success view:
    if view is 'success':

        # confirmed: test flag
        if (
                'flags' not in request.session or
                'confirmed' not in request.session['flags']):
            return HTTPFound(location=request.route_url('party'))

        if 'appstruct' not in request.session:
            return HTTPFound(location=request.route_url('party'))

    # finished view:
    if view is 'finished':

        # check if db entry exists
        if not PartyTicket.has_token(userdata['token']):
            return HTTPFound(location=request.route_url('party'))
        return
    return
