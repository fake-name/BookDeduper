
import os.path
import bs4
from . import base


class HtmlInterface(base.BookInterface):

	@staticmethod
	def wants_file(file_path):
		_, ext = os.path.splitext(file_path)
		return ext.lower() == ".html" or ext.lower() == ".htm"

	def open_file(self, file_path):
		with open(file_path, "r") as fp:
			markup = fp.read()

		soup = bs4.BeautifulSoup(markup, 'lxml')
		self.text = soup.get_text(strip=True)


	def get_text(self):
		return self.text

	def get_images(self):
		return []

