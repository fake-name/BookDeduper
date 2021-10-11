
import os.path
import logging
import io
import bs4
from PIL import Image
from . import base

import util.lit.reader as lit_reader

def parse_opf(opf_ctnt):
	pass


class LitInterface(base.BookInterface):

	@staticmethod
	def wants_file(file_path):
		_, ext = os.path.splitext(file_path)
		return ext.lower() == ".lit"

	def open_file(self, file_path):
		log = logging.getLogger(self.__class__.__name__)
		reader = lit_reader.LitContainer(file_path, log)

		self.images = []
		self.texts = []

		filenames = reader.namelist()
		for filename in filenames:
			fctnt = reader.read(filename)
			lfn = filename.lower()
			if any([lfn.endswith(im_ext) for im_ext in ['.jpg', '.png', 'jpeg', '.gif', '.bmp']]):
				bio = io.BytesIO(fctnt)
				image = Image.open(bio)
				self.images.append(image)

			if any([lfn.endswith(htm_ext) for htm_ext in ['.html', '.htm']]):
				soup = bs4.BeautifulSoup(fctnt, 'lxml')
				self.texts.append(soup.get_text(strip=True))

	def get_text(self):
		return "\n\n".join(self.texts)

	def get_images(self):
		return self.images

