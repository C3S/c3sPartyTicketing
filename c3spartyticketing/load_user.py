# -*- coding: utf-8 -*-
"""
This module holds functionality to interact with c3sMembership.
"""

import json
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
import requests
from requests import ConnectionError

from c3spartyticketing.models import PartyTicket


@view_config(route_name='load_user')
def load_user(request):
    '''
    A view for all members with invitation link from invitation email.

    Receive link containing **token** and load user details.

    Saves details in userdata.

    Userdata should only be changed in this view.

    *load_user* is the only entrance door.
    '''
    print('--- load user ---------------------------------------------------')

    _token = request.matchdict['token']
    _email = request.matchdict['email']

    # ## clear session
    request.session['userdata'] = {}
    request.session['derivedvalues'] = {}
    request.session['flags'] = {}
    # XXX think about a nicer abstract way to save derived values (->form
    # object) and flags, which control the flow

    # distinction member / nonmember
    request.session['flags']['isMember'] = True

    # ## load userdata from dbentry
    _ticket = PartyTicket.get_by_token(_token)
    print('searching db for user ...')
    try:
        if isinstance(_ticket, PartyTicket):
            assert(_ticket.token == _token)
            assert(_ticket.email == _email)
            print "found a valid dbentry (id: {})".format(_ticket.id)
            userdata = {
                'token': _ticket.token,
                'id': _ticket.id,
                'firstname': _ticket.firstname,
                'lastname': _ticket.lastname,
                'email': _ticket.email,
                'mtype': _ticket.membership_type,
                'is_legalentity': _ticket.is_legalentity,
                'email_confirm_code': _ticket.email_confirm_code
            }
            request.session['userdata'] = userdata
            return HTTPFound(location=request.route_url('party'))
    except:
        print "no valid dbentry found."
        pass

    # ## load userdata from membership app
    data = json.dumps({"token": _token})
    # print(data)
    try:
        print('querying MGV API ...')
        _auth_header = {
            'X-Messaging-Token': request.registry.settings['yes_auth_token']
        }
        res = requests.put(
            request.registry.settings['yes_api_url'],
            data,
            headers=_auth_header,
            verify=False,
        )
        print("REMOVE verify=False IN load_user!!! JUST FOR TESTING!!!!!!!!!!!!!!!!")
    except ConnectionError, ce:
        print("we hit a ConnectionError. report to staff immediately!")
        mailer = get_mailer(request)
        message_to_staff = Message(
            subject="[ALERT] c3sPartyTicketing reports ConnectionError!",
            sender=request.registry.settings['c3spartyticketing.mail_sender'],
            recipients=[
                request.registry.settings['c3spartyticketing.mail_rec']],
            body="""{}

                 """.format(ce)
        )
        if 'true' in request.registry.settings['testing.mail_to_console']:
            # ^^ yes, a little ugly, but works; it's a string
            # print "printing mail"
            print(
                message_to_staff.subject,
                message_to_staff.body,
            )
        else:
            # print "sending mail"
            mailer.send(message_to_staff)

        request.session.flash(
            """Sorry, there was a problem loading your data from the membership registry.
            We notified staff about this.
            """,
            'message_to_user'
        )
        return HTTPFound(request.route_url('error_page'))

    # print u"the result: {}".format(res)
    # print u"the result.json(): {}".format(res.json())
    # print u"the result.reason: {}".format(res.reason)
    # print u"dir(res): {}".format(dir(res))
    try:
        userdata = {
            'token': _token,
            'id': 'None',
            'firstname': res.json()['firstname'],
            'lastname': res.json()['lastname'],
            'email': res.json()['email'],
            'mtype': res.json()['mtype'],
            'is_legalentity': res.json()['is_legalentity'],
        }
        assert(res.json()['email'] == _email)
        request.session['userdata'] = userdata
        return HTTPFound(location=request.route_url('party'))
    except:
        print('no valid entry found. redirecting ...')
        pass

    return HTTPFound(
        location=request.registry.settings['registration.access_denied_url']
    )
