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
from selenium import webdriver


class Server(object):

	# singleton
	_instance = None
	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Server, cls).__new__(cls, *args, **kwargs)
		return cls._instance

	def connect(self, cfg, customAppSettings={}):
		self.cfg = cfg
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
		self.db = DBSession
		Base.metadata.create_all(engine)
		from c3spartyticketing import main
		app = main({}, **self.appSettings)
		# create srv
		self.srv = StopableWSGIServer.create(
			app, 
			host=self.cfg['app']['host'],
			port=self.cfg['app']['port']
		)
		# store some derived variables
		self.srv.url = 'http://' + self.cfg['app']['host'] + ':' \
			+ self.cfg['app']['port'] + '/'
		self.srv.lu = 'lu/' + self.cfg['member']['token'] + '/' \
			+ self.cfg['member']['email']
		# check srv
		if not self.srv.wait():
			raise Exception('Server could not be fired up. Exiting ...')
		return self.srv

	def disconnect(self):
		self.db.close()
		self.db.remove()
		os.remove(self.cfg['app']['db'])
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