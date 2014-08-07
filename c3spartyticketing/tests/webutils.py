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

	def connect(self, cfg):
		self.cfg = cfg
		# app
		self.appSettings = appconfig(
			'config:' + os.path.join(
				os.path.dirname(__file__), '../../', cfg['app']['ini']
			)
		)
		self.appSettings['sqlalchemy.url'] = 'sqlite:///'+cfg['app']['db']
		# XXX: merge self.appSettings and cfg['app']['appSettings']
		engine = engine_from_config(self.appSettings)
		DBSession.configure(bind=engine)
		self.db = DBSession
		Base.metadata.create_all(engine)
		from c3spartyticketing import main
		app = main({}, **self.appSettings)
		# create srv
		self.srv = StopableWSGIServer.create(
			app, 
			host=cfg['app']['host'],
			port=cfg['app']['port']
		)
		# store some derived variables
		self.srv.url = 'http://' + cfg['app']['host'] + ':' \
			+ cfg['app']['port'] + '/'
		self.srv.lu = 'lu/' + cfg['member']['token'] + '/' \
			+ cfg['member']['email']
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