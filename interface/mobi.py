


import os.path
from . import base


class MobiInterface(base.BookInterface):


	@staticmethod
	def wants_file(file_path):
		_, ext = os.path.splitext(file_path)
		return ext.lower() == ".mobi"