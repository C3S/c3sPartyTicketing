# configuration of testing framework
cfg = {
	'app': {
		'host': '0.0.0.0',
		'port': '6544',
		'db': 'tests.db',
		'ini': "development.ini",
		'appSettings': {},
	},
	'webdriver': {
		#'driver': webdriver.PhantomJS(), # XXX init not here
		'desired_capabilities': {} # XXX: override default
	},
	'member': {
		'token': 'OQ157KBFWH',
		'firstname': 'TestFirstname',
		'lastname': 'TestLastname',
		'email': 'alexander.blum@c3s.cc',
		'membership_type': 'normal',
	},
	'staff': {
		'login': u'rut', 
		'password': u'berries', 
		'email': u'rut@test.c3s.cc',
	},
	'dbg': {
		'logSection': True,
		'screenshot': True,
		'screenshotPath': './c3spartyticketing/tests/screenshots/'
	}
}