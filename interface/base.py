
import abc
import logging

class BookInterface(object, metaclass=abc.ABCMeta):
	def __init__(self, file_path):
		self.log = logging.getLogger("Main." + self.__class__.__name__)
		self.open_file(file_path)

	@staticmethod
	@abc.abstractmethod
	def wants_file(file_path):
		pass

	@abc.abstractmethod
	def open_file(self, file_path):
		pass

	@abc.abstractmethod
	def get_text(self):
		pass

	@abc.abstractmethod
	def get_images(self):
		pass

