import os
from sqlalchemy import engine_from_config
from c3spartyticketing.models import (
	DBSession,
	Base,
	PartyTicket,
	C3sStaff,
	Group,
)
from paste.deploy.loadwsgi import appconfig
from webtest.http import StopableWSGIServer
from webtest import TestApp
from selenium import webdriver


class Server(object):

	# singleton
	_instance = None
	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Server, cls).__new__(cls, *args, **kwargs)
		return cls._instance

	def connect(self, cfg, customAppSettings={}, wrapper='StopableWSGIServer'):
		self.cfg = cfg
		# clear old connections
		# try:
		# 	DBSession.close()
		# 	DBSession.remove()
		# 	os.remove(self.cfg['app']['db'])
		# except:
		# 	pass
		# create appConfig from ini
		self.appSettings = appconfig(
			'config:' + os.path.join(
				os.path.dirname(__file__), '../../', self.cfg['app']['ini']
			)
		)
		# store some derived variables
		self.appSettings['sqlalchemy.url'] = 'sqlite:///'+self.cfg['app']['db']
		# merge/override appConfig with custom settings in cfg
		self.appSettings.update(self.cfg['app']['appSettings'])
		# merge/override appConfig with individual custom settings
		self.appSettings.update(customAppSettings)
		# app
		engine = engine_from_config(self.appSettings)
		DBSession.configure(bind=engine)
		Base.metadata.create_all(engine)
		from c3spartyticketing import main
		app = main({}, **self.appSettings)
		# create srv
		if wrapper == 'StopableWSGIServer':
			self.srv = StopableWSGIServer.create(
				app, 
				host=self.cfg['app']['host'],
				port=self.cfg['app']['port']
			)
			# check srv
			if not self.srv.wait():
				raise Exception('Server could not be fired up. Exiting ...')
		elif wrapper == 'TestApp':
			self.srv = TestApp(app)
		else:
			raise Exception('Wrapper could not be found. Exiting ...')
		# store some variables
		self.srv.db = DBSession
		self.srv.url = 'http://' + self.cfg['app']['host'] + ':' \
			+ self.cfg['app']['port'] + '/'
		self.srv.lu = 'lu/' + self.cfg['member']['token'] + '/' \
			+ self.cfg['member']['email']
		return self.srv

	def disconnect(self):
		self.srv.db.close()
		self.srv.db.remove()
		os.remove(self.cfg['app']['db'])
		if isinstance(self.srv, StopableWSGIServer):
			self.srv.shutdown()


class Client(object):

	# singleton
	_instance = None
	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance =	super(Client, cls).__new__(cls, *args, **kwargs)
		return cls._instance

	def connect(self, cfg):
		self.cfg = cfg
		self.cli = webdriver.PhantomJS() # Firefox()
		return self.cli

	def disconnect(self):
		self.cli.quit()