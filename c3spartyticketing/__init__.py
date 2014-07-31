from pyramid.config import Configurator
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config

from c3spartyticketing.security.request import RequestWithUserAttribute
from c3spartyticketing.security import (
    Root,
    groupfinder
)

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .models import (
    DBSession,
    Base,
)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # database
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    # sessioning
    session_factory = session_factory_from_settings(settings)
    authn_policy = AuthTktAuthenticationPolicy(
        's0secret!!',
        callback=groupfinder,)
    authz_policy = ACLAuthorizationPolicy()

    # config
    config = Configurator(settings=settings,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy,
                          root_factory=Root,
                          session_factory=session_factory,)
    # using a custom request with user information
    config.set_request_factory(RequestWithUserAttribute)
    config.include('pyramid_chameleon')  # templating
    config.include('pyramid_mailer')  # mailings
    config.add_translation_dirs(
        'colander:locale/',
        'deform:locale/',
        'c3spartyticketing:locale/')
    config.add_static_view('static_deform', 'deform:static')
    config.add_subscriber('c3spartyticketing.subscribers.add_base_template',
                          'pyramid.events.BeforeRender')
    config.add_subscriber('c3spartyticketing.subscribers.add_locale_to_cookie',
                          'pyramid.events.NewRequest')
    config.add_static_view('static', 'static', cache_max_age=3600)
    # user views
    config.add_route('load_user', '/lu/{token}/{email}')
    config.add_route('party', '/')  # the landing page
    config.add_route('confirm', '/confirm')  # shows entered data f. correction
    config.add_route('success', '/success')  # shows success info
    #config.add_route('sendmail', '/check_email')
    config.add_route('finished', '/finished') # if registration is over
    config.add_route('verify_email_password', '/verify/{email}/{code}')
    config.add_route('success_pdf', '/C3S_Ticket_{namepart}.pdf')
    # backend/staff
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('all_codes', '/all_codes')
    config.add_route('dashboard', '/dashboard/{number}')
    config.add_route('stats', '/stats')
    config.add_route('print', '/print')
    config.add_route('detail', '/detail/{ticket_id}')
    config.add_route('edit_ticket', '/edit_ticket/{ticket_id}')
    config.add_route('send_ticket_mail', '/ticketmail/{ticket_id}')
    config.add_route('get_ticket', '/ticket/{email}/c3sPartyTicket_{code}')
    config.add_route('get_ticket_mobile',
                     '/mticket/{email}/c3sPartyTicket_{code}')
    config.add_route('give_ticket', '/give_ticket/c3sPartyTicket_{code}')
    config.add_route('new_ticket', '/new_ticket')
    config.add_route('hobo', '/hobo')  # new hobo / schwarzfahrer
    config.add_route('switch_pay', '/switch_pay/{ticket_id}')
    config.add_route('delete_entry', '/delete/{ticket_id}')
    # staff eat staff
    config.add_route('staff', '/staff')
    # cashier
    config.add_route('kasse', '/kasse')
    config.add_route('k', '/k')
    config.add_route('check_in', '/ci/{event}/{code}')
    config.scan()
    return config.make_wsgi_app()
