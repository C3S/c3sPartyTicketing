# -*- coding: utf-8 -*-
"""
This module holds views with accountants functionality.

Staff can

* log in (**accountants_login**)
* log out (**logout_view**)
"""
import colander
import deform
from deform import ValidationFailure
from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
    authenticated_userid,
)
from pyramid.url import route_url
from pyramid.view import view_config
from translationstring import TranslationStringFactory

from c3spartyticketing.models import C3sStaff

_ = TranslationStringFactory('c3spartyticketing')

LOGGING = True

if LOGGING:  # pragma: no cover
    import logging
    log = logging.getLogger(__name__)


@view_config(renderer='templates/login.pt',
             route_name='login')
def accountants_login(request):
    """
    This view lets accountants log in.

    After successful login, staff are redirected to the dashboard.
    Visiting this view when already logged in also redirects there.

    The form submits to this view, so errors are rendered nearby.

    Template used:
        templates/login.pt

    Returns:
        | the form, rendered in a template,
        | or a redirect to the dashboard.
    """
    # print(request)
    logged_in = authenticated_userid(request)
    # print("authenticated_userid: " + str(logged_in))

    log.info("login by %s" % logged_in)

    if logged_in is not None:  # if user is already authenticated
        return HTTPFound(  # redirect her to the dashboard
            request.route_url('dashboard',
                              number=0,))

    class AccountantLogin(colander.MappingSchema):
        """
        colander schema for login form
        """
        login = colander.SchemaNode(
            colander.String(),
            title="login",
            oid="login",
        )
        password = colander.SchemaNode(
            colander.String(),
            validator=colander.Length(min=5, max=100),
            widget=deform.widget.PasswordWidget(size=20),
            title="password",
            oid="password",
        )

    schema = AccountantLogin()

    form = deform.Form(
        schema,
        buttons=[
            deform.Button('submit', u'Submit'),
            deform.Button('reset', u'Reset')
        ],
        # use_ajax=True,
        # renderer=zpt_renderer
    )

    # if the form has been used and SUBMITTED, check contents
    if 'submit' in request.POST:
        # print("the form was submitted")
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure, e:
            print(e)

            request.session.flash(
                _(u"Please note: There were errors, "
                  "please check the form below."),
                'message_above_form',
                allow_duplicate=False)
            return{'form': e.render()}

        # get user and check pw...
        login = appstruct['login']
        password = appstruct['password']

        try:
            checked = C3sStaff.check_password(login, password)
        except AttributeError:  # pragma: no cover
            checked = False
        if checked:
            log.info("password check for %s: good!" % login)
            headers = remember(request, login)
            log.info("logging in %s" % login)
            return HTTPFound(  # redirect to accountants dashboard
                location=route_url(  # after successful login
                    'dashboard',
                    number=0,
                    request=request),
                headers=headers)
        else:
            log.info("password check: failed.")

    html = form.render()
    return {'form': html, }


@view_config(permission='view',
             route_name='logout')
def logout_view(request):
    """
    can be used to log a user/staffer off. "forget"
    """
    request.session.invalidate()
    request.session.flash(u'Logged out successfully.')
    headers = forget(request)
    return HTTPFound(location=route_url('login', request),
                     headers=headers)
