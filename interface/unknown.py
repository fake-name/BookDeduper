
from . import base


class UnknownInterface(base.BookInterface):


	@staticmethod
	def wants_file(file_path):
		return True

	def known_file(self):
		return False


	def open_file(self, file_path):
		pass

	def get_text(self):
		raise RuntimeError("Cannot get text from an unknown file")

	def get_images(self):
		raise RuntimeError("Cannot get images from an unknown file")

