
import os.path
from . import base


class TextInterface(base.BookInterface):

	@staticmethod
	def wants_file(file_path):
		_, ext = os.path.splitext(file_path)
		return ext.lower() == ".txt"

	def open_file(self, file_path):
		with open(file_path, "r") as fp:
			self.text = fp.read()

	def get_text(self):
		return self.text

	def get_images(self):
		return []

