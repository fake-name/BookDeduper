
import sys
import os
import os.path
import traceback

import interface

modules = [
	interface.Azw3Interface,
	interface.EpubInterface,
	interface.MobiInterface,
	interface.PdfInterface,
]

def try_load_file(file_path):
	try:
		for module in modules:
			if module.wants_file(file_path):
				return module(file_path)
	except Exception:
		traceback.print_exc()
		print("Bad file: '%s'" % (file_path, ))
	print("Unknown: ", file_path)
	return interface.UnknownInterface(file_path)

def scan_directory(path):
	items = []

	for root, directories, files in os.walk(path):
		for filen in files:
			if filen == "metadata.opf":
				continue
			if filen == "cover.jpg":
				continue


			fqpath = os.path.join(root, filen)
			loaded = try_load_file(fqpath)
			if loaded.known_file():
				loaded.get_text()
				loaded.get_images()
			# items.append(loaded)



def go():
	if len(sys.argv) != 2:
		print("No path!")
		sys.exit(1)

	if not os.path.exists(sys.argv[1]):
		print("Path '%s' doesn't exist!", sys.argv[1])
		sys.exit(2)

	scan_directory(sys.argv[1])

if __name__ == '__main__':
	import util.logSetup
	util.logSetup.initLogging()
	go()
