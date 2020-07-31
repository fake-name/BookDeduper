
import os.path
import io
import logging
import struct
from PIL import Image
from PIL import ImageOps

import poppler
import PyPDF2
from . import base


# From https://gist.github.com/gstorer/f6a9f1dfe41e8e64dcf58d07afa9ab2a
img_modes = {'/DeviceRGB': 'RGB', '/DefaultRGB': 'RGB',
						 '/DeviceCMYK': 'CMYK', '/DefaultCMYK': 'CMYK',
						 '/DeviceGray': 'L', '/DefaultGray': 'L',
						 '/Indexed': 'P'}


def tiff_header_for_CCITT(width, height, img_size, CCITT_group=4):
	# http://www.fileformat.info/format/tiff/corion.htm
	fields = 8
	tiff_header_struct = '<' + '2s' + 'H' + 'L' + 'H' + 'HHLL' * fields + 'L'
	return struct.pack(tiff_header_struct,
						b'II',  # Byte order indication: Little indian
						42,  # Version number (always 42)
						8,  # Offset to first IFD
						fields,  # Number of tags in IFD
						256, 4, 1, width,  # ImageWidth, LONG, 1, width
						257, 4, 1, height,  # ImageLength, LONG, 1, lenght
						258, 3, 1, 1,  # BitsPerSample, SHORT, 1, 1
						259, 3, 1, CCITT_group,  # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
						262, 3, 1, 0,  # Threshholding, SHORT, 1, 0 = WhiteIsZero
						# StripOffsets, LONG, 1, len of header
						273, 4, 1, struct.calcsize(tiff_header_struct),
						278, 4, 1, height,  # RowsPerStrip, LONG, 1, length
						279, 4, 1, img_size,  # StripByteCounts, LONG, 1, size of image
						0  # last IFD
						)


def extract_images_from_pdf_page(xObject):

	# Check if the page has objects
	try:
		xObject = xObject['/Resources']['/XObject'].getObject()
	except KeyError:
		return []

	image_list = []

	for obj in xObject:
		if xObject[obj]['/Subtype'] == '/Image':
			size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
			# getData() does not work for CCITTFaxDecode or DCTDecode
			# as of 1 Aug 2018. Not sure about JPXDecode.
			data = xObject[obj]._data

			color_space = xObject[obj]['/ColorSpace']
			if '/FlateDecode' in xObject[obj]['/Filter']:
				if isinstance(color_space, PyPDF2.generic.ArrayObject) and color_space[0] == '/Indexed':
					color_space, color_base, _hival, lookup = [v.getObject() for v in color_space] # pg 262
				mode = img_modes[color_space]

				data = xObject[obj].getData() # need to use getData() here
				img = Image.frombytes(mode, size, data)
				if color_space == '/Indexed':
					img.putpalette(lookup.getData())
					img = img.convert('RGB')
				imgByteArr = io.BytesIO()
				img.save(imgByteArr,format='PNG')
				imgByteArr.seek(0)

				image_list.append(base.ImageBytes(data=imgByteArr.read(),
								     format='PNG',
								     image_name=obj[1:]))

			elif '/DCTDecode' in xObject[obj]['/Filter']:
				image_list.append(base.ImageBytes(data=data,
								     format='JPG',
								     image_name=obj[1:]))
			elif '/JPXDecode' in xObject[obj]['/Filter']:
				image_list.append(base.ImageBytes(data=data,
								     format='JP2',
								     image_name=obj[1:]))
			elif '/CCITTFaxDecode' in xObject[obj]['/Filter']:
				if xObject[obj]['/DecodeParms']['/K'] == -1:
					CCITT_group = 4
				else:
					CCITT_group = 3
				data = xObject[obj]._data
				img_size = len(data)
				tiff_header = tiff_header_for_CCITT(
					size[0], size[1], img_size, CCITT_group)
				im = Image.open(io.BytesIO(tiff_header + data))

				if xObject[obj].get('/BitsPerComponent') == 1:
					# experimental condition
					# http://users.fred.net/tds/leftdna/sciencetiff.html
					im = ImageOps.flip(im)

				imgByteArr = io.BytesIO()
				im.save(imgByteArr,format='PNG')
				imgByteArr.seek(0)
				image_list.append(base.ImageBytes(data=imgByteArr.read(),
								     format='PNG',
								     image_name=obj[1:]))
			else:
				print ('Unhandled image type: {}'.format(xObject[obj]['/Filter']))
		else:
			image_list += extract_images_from_pdf_page(xObject[obj])

	return image_list
class PdfInterface(base.BookInterface):

	def __init__(self, *args, **kwargs):
		super(PdfInterface, self).__init__(*args, **kwargs)

		# PDFMiner logs A LOT. Shut that up.
		logging.getLogger("pdfminer").setLevel(logging.WARNING)

	@staticmethod
	def wants_file(file_path):
		_, ext = os.path.splitext(file_path)
		return ext.lower() == ".pdf"


	def __load_text(self):
		self.texts = []
		for page_num in range(self.p_pdf.pages):
			page = self.p_pdf.create_page(page_num)

			text = page.text()

			# extract_text() can return None, we don't want to strip that.
			if text:
				text = text.strip()

			if text:
				self.texts.append(text)


		self.log.info("Found %s pages of text consisting of %s total characters.", len(self.texts), sum([len(tmp) for tmp in self.texts]))


	def __load_images(self):
		self.images = []
		for page_num in range(self.pdf.getNumPages()):
			page = self.pdf.getPage(page_num)

			images = extract_images_from_pdf_page(page)
			for image in images:
				self.images.append(image)

		self.log.info("Found %s images.", len(self.images))


	def open_file(self, file_path):

		self.log.info("Loading file: %s", file_path)

		# Yes, we use two different libraries to process the PDF.
		# pdfplumber and PyPDF2 both work, but take 100+ times longer
		# to extract text. Poppler is ~1-2 seconds for 400 pages, pyPDF2
		# is ~200+ seconds
		self.p_pdf = poppler.load_from_file(file_path)
		self.__load_text()

		self.fh = open(file_path, "rb")
		self.pdf = PyPDF2.PdfFileReader(self.fh)

		self.__load_images()

	def get_text(self):

		return self.texts

	def get_images(self):
		ret = []

		for image in self.images:
			bio = io.BytesIO(image.data)
			image = Image.open(bio)
			ret.append(image)

		return ret
