
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

		self.log.info("Found %s sections of %s total characters.", len(self.texts), sum([len(tmp) for tmp in self.texts]))

	def __load_images(self):
		self.images = []

		for imageobj in self.epub.get_items_of_type(ebooklib.ITEM_IMAGE):

			self.images.append(
					base.ImageBytes(data=imageobj.content,
								     format='',
								     image_name='')
				)

		self.log.info("Found %s images.", len(self.images))

	def open_file(self, file_path):
		self.log.info("Loading file: %s", file_path)
		self.epub = ebooklib.epub.read_epub(file_path)
		self.__load_text()
		self.__load_images()

	def get_text(self):
		return "\n\n".join(self.texts)

	def get_images(self):
		ret = []

		for image in self.images:
			bio = io.BytesIO(image.data)
			image = Image.open(bio)
			ret.append(image)

		return ret

