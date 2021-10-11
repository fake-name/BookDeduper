

import logging
import pickle
import apsw
import json

class DbInterface():
	def __init__(self, save_path):
		self.log = logging.getLogger("Main.DB")

		self.db = apsw.Connection(save_path)
		self.check_init_db()

	def check_init_db(self):
		cur = self.db.cursor()

		cur.execute("""
			CREATE TABLE IF NOT EXISTS cache_files
			(
				fspath        text,
				internal_path text,
				content       text,
				meta          text,
				UNIQUE(fspath, internal_path)
			);
			""")
		cur.execute("""
			CREATE TABLE IF NOT EXISTS key_value
			(key text UNIQUE, value text);
			""")

	def insert_kv(self, key, value):

		cur = self.db.cursor()
		cur.execute("""
			INSERT OR REPLACE INTO key_value (key, value)
			VALUES (?, ?)
			""", (key, json.dumps(value)))
		cur.execute("COMMIT;")


	def get_kv(self, key):

		cur = self.db.cursor()
		cur.execute("""
			SELECT (value) FROM key_value
			WHERE (key = ?)
			""", (key, ))
		res = cur.fetchone()
		cur.execute("COMMIT;")

		if res:
			return json.loads(res[0])
		else:
			return None


	def have_kv(self, key):
		cur = self.db.cursor()
		cur.execute("""
			SELECT COUNT(*) FROM key_value
			WHERE key = ?;
			""", (key, ))
		res = cur.fetchone()
		cur.execute("COMMIT;")

		return res[0]

	def get_file(self, fspath, internal_path=""):
		cur = self.db.cursor()
		cur.execute("""
			SELECT fspath, internal_path, content, meta FROM cache_files
			WHERE fspath = ? AND internal_path = ?;
			""", (fspath, internal_path))
		res = cur.fetchone()
		cur.execute("COMMIT;")
		if res:
			fspath, internal_path, content, meta  = res
			return {
				"fspath"        : fspath,
				"internal_path" : internal_path,
				"content"       : pickle.loads(content),
				"meta"          : json.loads(meta),
			}
		return None

	def have_file(self, fspath, internal_path=""):
		cur = self.db.cursor()
		cur.execute("""
			SELECT COUNT(*) FROM cache_files
			WHERE fspath = ? AND internal_path = ?;
			""", (fspath, internal_path))
		res = cur.fetchone()
		cur.execute("COMMIT;")

		return res[0]

	def insert_file(self, fspath, content, internal_path="", meta=None):
		# self.log.info("Saving key: %s -> %s", fspath, internal_path)

		cur = self.db.cursor()

		cur.execute("""
			INSERT OR REPLACE INTO cache_files (fspath, internal_path, content, meta)
			VALUES (?, ?, ?, ?)
			""", (fspath, internal_path, pickle.dumps(content), json.dumps(meta)))

		cur.execute("COMMIT;")

	def get_page_count(self):

		cur = self.db.cursor()
		cur.execute("""
			SELECT count(1) FROM cache_files;
			""")
		res = cur.fetchone()
		cur.execute("COMMIT;")

		return res[0]

	def get_all_pages(self):
		cur = self.db.cursor()
		cur.execute("""
			SELECT fspath, internal_path, content, meta FROM cache_files
			""")

		ret = []
		for res in cur:
			fspath, internal_path, content, meta = res
			ret.append({
				"fspath"        : fspath,
				"internal_path" : internal_path,
				"content"       : pickle.loads(content),
				"meta"          : json.loads(meta),
			})

		cur.execute("COMMIT;")

		return ret
