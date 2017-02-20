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
        'venue_name': 'C3S Headquarter',
        'venue_shortname': 'C3SHQ',
        'city': u'Düsseldorf',
        'address': u'Rochusstraße 44, 40479 Düsseldorf',
        'public_transport': u'from central station use tram 707 (towards Unterrath S-Bahnhof, get off at Schloß Jägerhof)',
        'map_url': 'https://www.openstreetmap.org/directions?engine=graphhopper_foot&route=51.220%2C6.794%3B51.233%2C6.788#map=15/51.2264/6.7918'
    },
    'ga': {  # general assembly options
        'date': '2017-04-02',
        'time': '13:00',
        'end_time': '17:00',
        'venue_name': 'C3S Headquarter',
        'venue_shortname': 'C3SHQ',
        'city': u'Düsseldorf',
        'address': u'Rochusstraße 44, 40479 Düsseldorf',
        'public_transport': u'from central station use tram 707 (towards Unterrath S-Bahnhof, get off at Schloß Jägerhof)',
        'map_url': 'https://www.openstreetmap.org/directions?engine=graphhopper_foot&route=51.220%2C6.794%3B51.233%2C6.788#map=15/51.2264/6.7918'
    },
    'registration': {
        'end': '2017-03-31',
        'endgvonly': '2017-04-01',
        'finish_on_submit': False,
        'access_denied_url': '/barcamp',
        'invitation_date': '2017-01-31',
        'fully_paid_date': '2017-02-28',
    },
}
