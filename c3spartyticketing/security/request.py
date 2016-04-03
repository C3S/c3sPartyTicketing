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

from c3spartyticketing.event_config import cfg

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
    def access_denied_url(request):
        """Returns the url to show when access is denied
        """
        return cfg['registration']['access_denied_url']

    @reify
    def finish_on_submit(request):
        return cfg['registration']['finish_on_submit']

    # things that cost money or not
    @reify
    def bc_cost(request):
        """
        Returns the cost of the attendance to the barcamp
        """
        return cfg['bc']['cost']

    @reify
    def bc_food_cost(request):
        """
        Returns the cost of the food served at the barcamp
        """
        return cfg['bc']['food_cost']

    # supporter ticket options
    @reify
    def supporter_M(request):
        """
        Returns the cost of the food served at the barcamp
        """
        return cfg['support']['M_cost']

    @reify
    def supporter_L(request):
        """
        Returns the cost of the food served at the barcamp
        """
        return cfg['support']['L_cost']

    @reify
    def supporter_XL(request):
        """
        Returns the cost of the food served at the barcamp
        """
        return cfg['support']['XL_cost']

    @reify
    def supporter_XXL(request):
        """
        Returns the cost of the food served at the barcamp
        """
        return cfg['support']['XXL_cost']

    # dates
    @reify
    def fully_paid_date(request):
        """
        Returns the date (string) of last payment arrival formatted to locale.
        """
        return format_date(
            datetime.strptime(
                cfg['registration']['fully_paid_date'],
                '%Y-%m-%d').date(),
            request.locale_name)

    # registration dates
    @reify
    def registration_end(request):
        """
        Returns the registration end date string ('2016-04-14')
        """
        return format_date(
            datetime.strptime(
                request.registry.settings['registration.end'], '%Y-%m-%d').date(),
            request.locale_name)

    @reify
    def invitation_date(request):
        """
        Returns the email invitation date string ('2016-03-04')
        """
        return format_date(
            datetime.strptime(
                request.registry.settings['registration.invitation_date'], '%Y-%m-%d').date(),
            request.locale_name)

    # locations
    # hpz
    @reify
    def bc_address(request):
        """
        Returns the address of HPZ location
        """
        return cfg['bc']['address']

    @reify
    def bc_transport(request):
        """
        Returns the public transport info of HPZ location
        """
        return cfg['bc']['public_transport']

    @reify
    def bc_shortname(request):
        """
        Returns the short name of HPZ location
        """
        return cfg['bc']['venue_shortname']

    @reify
    def bc_name(request):
        """
        Returns the name of HPZ location
        """
        return cfg['bc']['venue_name']

    @reify
    def bc_city(request):
        """
        Returns the name of HPZ city, e.g. 'Düsseldorf'
        """
        return cfg['bc']['city']

    @reify
    def bc_map_url(request):
        """
        Returns the name of HPZ location
        """
        return cfg['bc']['map_url']

    # c3s hq
    @reify
    def ga_address(request):
        """
        Returns the address of HPZ location
        """
        return cfg['ga']['address']

    @reify
    def ga_transport(request):
        """
        Returns the public transport info of HPZ location
        """
        return cfg['ga']['public_transport']

    @reify
    def ga_venue_shortname(request):
        """
        Returns the short name of HPZ location
        """
        return cfg['ga']['venue_shortname']

    @reify
    def ga_venue_name(request):
        """
        Returns the name of HPZ location
        """
        return cfg['ga']['venue_name']

    @reify
    def ga_city(request):
        """
        Returns the name of HPZ city, e.g. 'Düsseldorf'
        """
        return cfg['ga']['city']

    @reify
    def ga_map_url(request):
        """
        Returns the name of HPZ location
        """
        return cfg['ga']['map_url']


    # BarCamp
    @reify
    def barcamp_date(request):
        """
        Returns the BarCamp Date string ('2016-04-16') formatted to locale.
        """
        return format_date(
            datetime.strptime(cfg['bc']['date'], '%Y-%m-%d').date(),
            request.locale_name)

    @reify
    def barcamp_timespan(request):
        """
        Returns the BarCamp duration string ('1pm - 5pm') formatted to locale.
        """
        return (u"{} -- {}".format(
            format_time(  # format start time to locale
                datetime.strptime(  # parse from settings string
                    cfg['bc']['time'], '%H:%M').time(),
                request.locale_name),
            format_time(  # format end time to locale
                datetime.strptime(  # parse from settings string
                    cfg['bc']['end_time'], '%H:%M').time(),
                request.locale_name)
        ))

    @reify
    def barcamp_time(request):
        """
        Returns the BarCamp start time ('12:00')
        """
        return cfg['bc']['time']

    @reify
    def barcamp_counter(request):
        """
        Prepare a date string for the nonmember template for countdown.
        
        The string shall look like '2016/06/12 12:00'.
        """
        _date = dateutil.parser.parse(cfg['bc']['date']).date()
        _time = dateutil.parser.parse(cfg['bc']['time']).time()
        return _date.strftime('%Y/%m/%d') + ' ' + _time.strftime('%H:%M')

    # general assembly
    @reify
    def assembly_date(request):
        """
        Returns the Assembly Date string ('2016-04-16') formatted to locale.
        """
        return format_date(
            datetime.strptime(cfg['ga']['date'], '%Y-%m-%d').date(),
            request.locale_name)

    @reify
    def assembly_timespan(request):
        """
        Returns the Assembly duration string ('1pm - 5pm') formatted to locale.
        """
        return (u"{} -- {}".format(
            format_time(  # format start time to locale
                datetime.strptime(  # parse from settings string
                    cfg['ga']['time'], '%H:%M').time(),
                request.locale_name),
            format_time(  # format end time to locale
                datetime.strptime(  # parse from settings string
                    cfg['ga']['end_time'], '%H:%M').time(),
                request.locale_name)
        ))

    @reify
    def assembly_time(request):
        """
        Returns the Assembly start time ('12:00')
        """
        return cfg['ga']['time']

    @reify
    def assembly_counter(request):
        """
        Prepare a date string for the nonmember template for countdown.
        
        The string shall look like '2016/06/12 12:00'.
        """
        _date = dateutil.parser.parse(cfg['ga']['date']).date()
        _time = dateutil.parser.parse(cfg['ga']['time']).time()
        return _date.strftime('%Y/%m/%d') + ' ' + _time.strftime('%H:%M')
        
