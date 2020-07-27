
import os.path
import io
from PIL import Image
import bs4
import ebooklib.epub
import ebooklib
from . import base


class EpubInterface(base.BookInterface):

	@staticmethod
	def wants_file(file_path):
		_, ext = os.path.splitext(file_path)
		return ext.lower() == ".epub"

	def __load_text(self):

		self.texts = []
		for document in self.epub.get_items_of_type(ebooklib.ITEM_DOCUMENT):
			soup = bs4.BeautifulSoup(document.content, 'lxml')

			# Title seems to get injected into cover pages, and shows up in get_text()
			# as "title", which is super unhelpful.
			if soup.title:
				soup.title.decompose()

			text = soup.get_text(strip=True)

			if text:
				self.texts.append(text)

	def __load_images(self):
		self.images = []

		for imageobj in self.epub.get_items_of_type(ebooklib.ITEM_IMAGE):
			bio = io.BytesIO(imageobj.content)
			image = Image.open(bio)
			self.images.append(image)


	def open_file(self, file_path):
		self.epub = ebooklib.epub.read_epub(file_path)
		self.__load_text()
		self.__load_images()

	def get_text(self):

		return self.texts

	def get_images(self):
		return self.images