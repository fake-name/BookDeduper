
import traceback

from .azw3    import Azw3Interface
from .epub    import EpubInterface
from .mobi    import MobiInterface
from .pdf     import PdfInterface
from .txt     import TextInterface
from .lit     import LitInterface
from .unknown import UnknownInterface

_functional_formats = [
	Azw3Interface,
	EpubInterface,
	# MobiInterface,
	PdfInterface,
	TextInterface,
	LitInterface,
]


def try_load_file(file_path):
	try:
		for module in _functional_formats:
			if module.wants_file(file_path):
				return module(file_path)
	except Exception:
		traceback.print_exc()
		print("Bad file: '%s'" % (file_path, ))
	print("Unknown: ", file_path)
	return UnknownInterface(file_path)
