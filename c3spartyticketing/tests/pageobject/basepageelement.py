from pageobject import client

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
	# implement: get text of WebElement
	def get(self):
		pass
	# implement: set text of WebElement
	def set(self, val):
		pass

# textfield
class TextfieldElement(BasePageElement):
	def __call__(self):
		return client.cli.find_element_by_id(self.locator)
	def get(self):
		return self().get_attribute("value")
	def set(self, val):
		self().send_keys(val)

# textarea
class TextareaElement(TextfieldElement):
	pass

# hidden
class HiddenElement(TextfieldElement):
	pass

# radiobutton
class RadiobuttonElement(BasePageElement):
	# returns radiobuttons
	def __call__(self):
		return client.cli.find_elements_by_name(self.locator)
	def get(self):
		for rb in self():
			if rb.is_selected():
				return rb.get_attribute("value")
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
	def set(self, val):
		if val is not self.get():
			self().click()