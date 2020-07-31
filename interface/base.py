
import abc
import logging
from collections import namedtuple

ImageBytes = namedtuple('ImageBytes', ['data', 'format','image_name'])

class BookInterface(object, metaclass=abc.ABCMeta):
	def __init__(self, file_path):
		self.log = logging.getLogger("Main." + self.__class__.__name__)
		self.__file_path = file_path
		self.open_file(file_path)

	def get_file_path(self):
		return self.__file_path

	def known_file(self):
		return True

	@staticmethod
	@abc.abstractmethod
	def wants_file(file_path):
		return False

	@abc.abstractmethod
	def open_file(self, file_path):
		pass

	@abc.abstractmethod
	def get_text(self):
		pass

	@abc.abstractmethod
	def get_images(self):
		pass

