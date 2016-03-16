#  -*- coding: utf-8 -*-
"""
This module holds functionality to enhance the app.
"""
# ### Making A 'User Object' Available as a Request Attribute
# docs.pylonsproject.org/projects/pyramid_cookbook/dev/authentication.html
from datetime import datetime
import dateutil
from pyramid.decorator import reify
from pyramid.request import Request
from pyramid.security import unauthenticated_userid

from c3spartyticketing.mail_utils import (
    format_date,
    format_time,
)
from c3spartyticketing.models import (
    C3sStaff,
)


class RequestWithUserAttribute(Request):
    """
    This class is used as replacement for the common Request class.

    It adds an important feature for c3sMembership: a request.user attribute,
    telling who is authenticated and using the app during this request.

    This is useful to protect some views to be used by staff only.
    """
    @reify
    def user(self):
        """
        The request.user attribute.

        Returns:
            * **id**, if user is known.
            * **None**, if user is not known.
        """
        userid = unauthenticated_userid(self)
        # print "--- in RequestWithUserAttribute: userid = " + str(userid)
        if userid is not None:
            # this should return None if the user doesn't exist
            # in the database
            # return dbsession.query('users').filter(user.user_id == userid)
            return C3sStaff.check_user_or_None(userid)
        # else: userid == None
        return userid  # pragma: no cover

        # /end of ### Making A 'User Object' Available as a Request Attribute


    @reify
    def supporter_M(request):
        """
        Returns the cost of the food served at the barcamp
        """
        return request.registry.settings['registration.supporter_M_cost']

    @reify
    def supporter_L(request):
        """
        Returns the cost of the food served at the barcamp
        """
        return request.registry.settings['registration.supporter_L_cost']

    @reify
    def supporter_XL(request):
        """
        Returns the cost of the food served at the barcamp
        """
        return request.registry.settings['registration.supporter_XL_cost']

    @reify
    def supporter_XXL(request):
        """
        Returns the cost of the food served at the barcamp
        """
        return request.registry.settings['registration.supporter_XXL_cost']

    @reify
    def fully_paid_date(request):
        """
        Returns the date (string) of last payment arrival formatted to locale.
        """
        return format_date(
            datetime.strptime(
                request.registry.settings['registration.fully_paid_date'],
                '%Y-%m-%d').date(),
            request.locale_name)

    # locations
    # hpz
    @reify
    def hpz_address(request):
        """
        Returns the address of HPZ location
        """
        # print(u"request.registry.settings['registration.hpz_address']"
        #      ".encode('utf-8'): {} ".format(
        #          request.registry.settings[
        #              'registration.hpz_address'].decode('utf-8')))

        return request.registry.settings[
            'registration.hpz_address'].decode('utf-8')

    @reify
    def hpz_transport(request):
        """
        Returns the public transport info of HPZ location
        """
        return request.registry.settings['registration.hpz_public_transport']

    @reify
    def hpz_shortname(request):
        """
        Returns the short name of HPZ location
        """
        return request.registry.settings['registration.hpz_shortname']

    @reify
    def hpz_name(request):
        """
        Returns the name of HPZ location
        """
        return request.registry.settings['registration.hpz_name']

    @reify
    def hpz_city(request):
        """
        Returns the name of HPZ city, e.g. 'Düsseldorf'
        """
        return request.registry.settings[
            'registration.hpz_city'].decode('utf-8')

    @reify
    def hpz_map_small(request):
        """
        Returns the name of HPZ location
        """
        return request.registry.settings['registration.hpz_map_small']

    @reify
    def hpz_map_URL(request):
        """
        Returns the name of HPZ location
        """
        return request.registry.settings['registration.hpz_map_URL']

    # c3s hq
    @reify
    def c3shq_address(request):
        """
        Returns the address of HPZ location
        """
        # print(u"request.registry.settings['registration.hpz_address']"
        #      ".encode('utf-8'): {} ".format(
        #          request.registry.settings[
        #              'registration.c3shq_address'].decode('utf-8')))

        return request.registry.settings[
            'registration.c3shq_address'].decode('utf-8')

    @reify
    def c3shq_transport(request):
        """
        Returns the public transport info of HPZ location
        """
        return request.registry.settings['registration.c3shq_public_transport']

    @reify
    def c3shq_shortname(request):
        """
        Returns the short name of HPZ location
        """
        return request.registry.settings['registration.c3shq_shortname']

    @reify
    def c3shq_name(request):
        """
        Returns the name of HPZ location
        """
        return request.registry.settings['registration.c3shq_name']

    @reify
    def c3shq_city(request):
        """
        Returns the name of HPZ city, e.g. 'Düsseldorf'
        """
        return request.registry.settings[
            'registration.c3shq_city'].decode('utf-8')

    @reify
    def c3shq_map_small(request):
        """
        Returns the name of HPZ location
        """
        return request.registry.settings['registration.c3shq_map_small']

    @reify
    def c3shq_map_URL(request):
        """
        Returns the name of HPZ location
        """
        return request.registry.settings['registration.c3shq_map_URL']

    # registration dates
    @reify
    def registration_end(request):
        """
        Returns the registration end date string ('2016-04-14')
        """
        return format_date(
            datetime.strptime(
                request.registry.settings['registration.end'],
                '%Y-%m-%d').date(),
            request.locale_name)

    @reify
    def invitation_date(request):
        """
        Returns the email invitation date string ('2016-03-04')
        """
        return format_date(
            datetime.strptime(
                request.registry.settings['registration.invitation_date'],
                '%Y-%m-%d').date(),
            request.locale_name)

    # BarCamp
    @reify
    def barcamp_date(request):
        """
        Returns the BarCamp Date string ('2016-04-16') formatted to locale.
        """
        return format_date(
            datetime.strptime(
                request.registry.settings['registration.bc_date'],
                '%Y-%m-%d').date(),
            request.locale_name)

    @reify
    def barcamp_timespan(request):
        """
        Returns the BarCamp duration string ('1pm - 5pm') formatted to locale.
        """
        return (u"{} -- {}".format(
            format_time(  # format start time to locale
                datetime.strptime(  # parse from settings string
                    request.registry.settings['registration.bc_time'],
                    '%H:%M').time(),
                request.locale_name),
            format_time(  # format end time to locale
                datetime.strptime(  # parse from settings string
                    request.registry.settings['registration.bc_end_time'],
                    '%H:%M').time(),
                request.locale_name)
        ))

    @reify
    def barcamp_duration_str(request):
        """
        Returns the BarCamp duration string ('12am - 8pm')
        """
        return request.registry.settings['registration.bc_duration_str']

    @reify
    def barcamp_time(request):
        """
        Returns the BarCamp start time ('12:00')
        """
        return request.registry.settings['registration.bc_time']

    @reify
    def barcamp_counter(request):
        """
        Prepare a date string for the nonmember template for countdown.
        
        The string shall look like '2016/06/12 12:00'.
        """
        _date = dateutil.parser.parse(
            request.registry.settings['registration.bc_date']).date()
        _time = dateutil.parser.parse(
            request.registry.settings['registration.bc_time']).time()
        string_for_counter = _date.strftime(
            '%Y/%m/%d') + ' ' + _time.strftime('%H:%M')
        return string_for_counter

    # general assembly
    @reify
    def assembly_date(request):
        """
        Returns the Assembly Date string ('2016-04-16') formatted to locale.
        """
        return format_date(
            datetime.strptime(
                request.registry.settings['registration.gv_date'],
                '%Y-%m-%d').date(),
            request.locale_name)

    @reify
    def assembly_timespan(request):
        """
        Returns the Assembly duration string ('1pm - 5pm') formatted to locale.
        """
        return (u"{} -- {}".format(
            format_time(  # format start time to locale
                datetime.strptime(  # parse from settings string
                    request.registry.settings['registration.gv_time'],
                    '%H:%M').time(),
                request.locale_name),
            format_time(  # format end time to locale
                datetime.strptime(  # parse from settings string
                    request.registry.settings['registration.gv_end_time'],
                    '%H:%M').time(),
                request.locale_name)
        ))

    @reify
    def assembly_time(request):
        """
        Returns the Assembly start time ('12:00')
        """
        return request.registry.settings['registration.gv_time']

    @reify
    def assembly_counter(request):
        """
        Prepare a date string for the nonmember template for countdown.
        
        The string shall look like '2016/06/12 12:00'.
        """
        _date = dateutil.parser.parse(
            request.registry.settings['registration.gv_date']).date()
        _time = dateutil.parser.parse(
            request.registry.settings['registration.gv_time']).time()
        string_for_counter = _date.strftime(
            '%Y/%m/%d') + ' ' + _time.strftime('%H:%M')
        return string_for_counter
        
