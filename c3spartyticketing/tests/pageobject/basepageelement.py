from pageobject import client
from selenium.common.exceptions import NoSuchElementException
import re

# base
class BasePageElement(object):

	# sets locator
	def __init__(self, locator):
		self.locator = locator
	# returns self
	def __get__(self, obj, cls=None):
		return self
	# synonym to set() for convenience
	def __set__(self, obj, val):
		self.set(val)
	# deactivates delete
	def __delete__(self, obj):
		pass

	# implement: return WebElement
	def __call__(self):
		pass
	# implement: get content of WebElement (deform field)
	def get(self):
		pass
	# implement: get content of WebElement (deform field readonly)
	def getRo(self):
		pass
	# implement: set content of WebElement (deform field)
	def set(self, val):
		pass

# textfield
class TextfieldElement(BasePageElement):
	def __call__(self):
		return client.cli.find_element_by_id(self.locator)
	def get(self):
		return self().get_attribute("value")
	def getRo(self):
		return self().text
	def set(self, val):
		tf = self()
		tf.clear()
		tf.send_keys(val)

# textarea
class TextareaElement(TextfieldElement):
	pass

# hidden
class HiddenElement(TextfieldElement):
	def getRo(self):
		return self.get()

# radiobutton
class RadiobuttonElement(BasePageElement):
	# returns radiobuttons
	def __call__(self):
		rb = client.cli.find_elements_by_name(self.locator)
		if not rb:
			raise NoSuchElementException()
		return rb
	def get(self):
		for rb in self():
			if rb.is_selected():
				return rb.get_attribute("value")
	# returns iterator of option
	def getRo(self):
		option = client.cli.find_elements_by_xpath(
			"//div[@id='item-"+self.locator+"']/div/p"
		)
		if len(option) == 1:
			return re.sub(
				self.locator+'-', '', 
				option[0].get_attribute("id")
			)
		return False
	# val: iterator of option
	def set(self, val):
		for rb in self():
			if rb.get_attribute("value") == val:
				rb.click()

# checkbox
class CheckboxElement(BasePageElement):
	def __call__(self):
		return client.cli.find_element_by_id(self.locator)
	def get(self):
		return self().is_selected()
	def getRo(self):
		try:
			self()
			return True
		except:
			return False
	def set(self, val):
		if val is not self.get():
			self().click()

# button
class ButtonElement(BasePageElement):
	def __call__(self):
		client.cli.find_element_by_id(self.locator).click()