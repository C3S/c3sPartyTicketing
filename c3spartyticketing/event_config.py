# -*- coding: utf-8 -*-
# some settings for the events

cfg = {
    'support': {  # supporter ticket options
        'M_cost': 5,
        'L_cost': 10,
        'XL_cost': 20,
        'XXL_cost': 50,
    },
    'bc': {  # barcamp options
        'cost': 0,
        'food_cost': 0,
        'date': '2017-04-01',
        'time': '13:00',
        'end_time': '19:00',
        'venue_name': 'C3S HQ',
        'venue_shortname': 'C3S HQ',
        'city': u'Düsseldorf',
        'address': u'Rochusstraße 44, D-40479 Düsseldorf',
        'public_transport': u'viele...',
        'map_url': 'https://www.openstreetmap.org/way/41265860'
    },
    'ga': {  # general assembly options
        'date': '2017-04-02',
        'time': '13:00',
        'end_time': '17:00',
        'venue_name': 'C3S HQ',
        'venue_shortname': 'C3S HQ',
        'city': u'Düsseldorf',
        'address': u'Rochusstraße 44, D-40479 Düsseldorf',
        'public_transport': u'viele...',
        'map_url': 'https://www.openstreetmap.org/way/41265860'
    },
    'registration': {
        'end': '2017-04-01',
        'endgvonly': '2017-04-02',
        'finish_on_submit': False,
        'access_denied_url': '/barcamp',
        'invitation_date': '2017-03-02',
        'fully_paid_date': '2017-04-02',
    },
}
