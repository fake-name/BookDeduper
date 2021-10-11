
import sys
import os
import os.path
import concurrent.futures
from io import BytesIO

import tqdm

import interface
import db_cache

def try_load(filename, db):

	loaded = interface.try_load_file(filename)
	if loaded.known_file():
		db.insert_file(filename, internal_path='text', content=loaded.get_text())
		for image_idx, image in enumerate(loaded.get_images()):
			im_bytes = BytesIO()
			image.save(im_bytes, 'jpeg')

			db.insert_file(filename,
				internal_path = 'image_{}'.format(image_idx),
				content       = im_bytes.getvalue()
				)


	loaded = interface.try_load_file(filename)
	if loaded.known_file():
		loaded.get_text()
		loaded.get_images()



def scan_directory(path):
	items = []
	exts = {}

	cache = db_cache.DbInterface("files.db")
	with concurrent.futures.ThreadPoolExecutor() as tpe:
		for root, directories, files in tqdm.tqdm(os.walk(path)):
			for filen in files:
				if filen == "metadata.opf":
					continue
				if filen == "cover.jpg":
					continue

				if filen.lower().endswith(".jpg"):
					continue

				_, ext = os.path.splitext(filen)

				fqpath = os.path.join(root, filen)

				res = tpe.submit(try_load, fqpath, cache)
				items.append(res)

				exts.setdefault(ext, 0)
				exts[ext] += 1

				if sum(exts.values()) % 1000 == 0:
					print("Found extensions: ", exts)

			if len(items) > 1000:
				for item in tqdm.tqdm(items):
					item.result()

	print("Found extensions: ", exts)



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
