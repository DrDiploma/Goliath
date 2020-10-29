import os, sqlite3, shutil, random, random, re, time, threading, sys, json, secrets
from requests import get
from os.path import join, basename, dirname
from queue import Queue

def timeit(func, *args, **kwargs):
	def timed(*args, **kwargs):
		it = time.time()
		result = func(*args, **kwargs)
		print('{} secs'.format(round(time.time()-it, 6)))
		return result
	return timed

def debug(func):
    def wrapper(*args,**kwargs):
        it = time.time()
        res = func(*args,**kwargs)
        secs = time.time()-it
        print('Function: {}\nSeconds: {}\nMinutes: {}\nArguments: {}\n'.format(
        	func.__name__, secs, secs/60, len(args)+len(kwargs)
        	)
        )
        return res
    return wrapper

# super class
class Nexus:
	@staticmethod
	def sleep(sec):
		time.sleep(sec)

	@staticmethod
	def gen_hex(x):
		return secrets.token_hex(x).upper()


	# file interactors
	@staticmethod
	def sep_url(url):
		return os.path.normpath(url).split(os.sep)

	@staticmethod
	def check_dirs_exist(folders):
		for dirname in folders:
			try:
				if not os.path.isdir(dirname): os.makedirs(dirname)
			except:
				print(f'{dirname} could not be made or is not a path')

	@staticmethod
	def check_dir_exist(dirname = ''):
		if not os.path.isdir(dirname): os.makedirs(dirname)

	@staticmethod
	def json_handle(filename = None, data = None, open_opt = None):
		if data and isinstance(filename, str):
			with open(filename, 'w') as j: json.dump(data, j, indent='\t')
		elif not data and isinstance(filename, str) and os.path.isfile(filename):
			with open(filename, 'r') as j: return json.load(j)
		elif data and isinstance(filename, str) and isinstance(open_opt, str):
			with open(filename, 'o') as j: json_dump(data, j, indent='\t')

	@staticmethod
	def file_handle(filename=None, opt=None, data=None):
		verify_name = isinstance(filename, str)
		if verify_name and opt=='w':
			with open(filename, 'w') as f: f.write(data)
		elif verify_name and opt=='r':
			with open(filename, 'r') as f: return f.read()
		elif verify_name and opt=='rm':
			with open(filename, 'r') as f: data = f.read()
			return sorted(list(set(data.split('\n'))), reverse=reverse)
		elif verify_name and opt=='wb':
			with open(filename, 'wb') as f: f.write(data)
		elif verify_name and opt=='rb':
			with open(filename, 'rb') as f: return f.read()


	@staticmethod
	def walk_path(path, exts=None):
		if isinstance(exts, list):
			return [join(path, d) for d in os.listdir(path) if os.path.splitext(d)[1][1:] in exts]
		else:
			return [join(path, d) for d in os.listdir(path)]


	# generators
	@staticmethod
	def replace_all(text, dic):
		for i, j in dic.items():
			text = text.replace(i, j)
		return text

	@staticmethod
	def find_in(needle, haystack):
		for hay in haystack:
			if needle in hay: return hay

	@staticmethod
	def date_(res = ['date', 'mtime', 'mdtime'], frmt_str = None):
		date_str = r'%d-%m-%Y'
		mtime_str = r'%H_%M_%S'
		if res == 'date': return time.strftime(date_str)
		elif res == 'mtime': return  time.strftime(mtime_str)
		elif res == 'mdtime': return  time.strftime(f'{mtime_str} {date_str}')
		elif isinstance(frmt_str, str): return time.strftime(frmt_str)
		

	# online
	@staticmethod
	def req(url):
		return str(get(url).content)

	@staticmethod
	def req_lines(url):
		for l in get(url, stream=True).iter_lines():
			yield l

	@staticmethod
	def regex(regex_patt, search_str, mode = 'find'):
		if mode == 'find': return re.findall(regex_patt, search_str)
		elif mode == 'search': return re.search(regex_patt, search_str)
		else: print('Not Implemented')

	@staticmethod
	def dl_file(url, filename = '', chunks = 1024):
		r = get(url, stream=True)
		if basename(filename) not in os.listdir(dirname(filename)):
			with open(filename, 'wb') as f:
				for chunk in r.iter_content(chunk_size=chunks):
					if chunk: f.write(chunk); f.flush()
			print(f'{filename} is finished')

	@staticmethod
	def thread_(func, tup=(), threads=3):
		q = Queue()
		def threader():
			while True: func(q.get()); q.task_done()

		for x in range(threads):
			t = threading.Thread(target=threader)
			t.daemon = True; t.start()

		for d in tup: q.put(d)
		q.join()

class Agilis:
	SQL = {
	'create': 'CREATE TABLE IF NOT EXISTS [{}] ({})',
	'insert': 'INSERT INTO [{}] ({}) VALUES ({})',
	'update': 'UPDATE {} SET {} WHERE {}',
	'select': 'SELECT {} FROM {}',
	'select where': 'SELECT {} FROM {} WHERE {}',
	'drop':'DROP TABLE {}'
	}

	def __init__(self, db_path):
		self.con = self.connect_db(db_path)

	def get_tables(self):
		self.cur_exec('''SELECT name FROM sqlite_master WHERE type='table' ; ''')
		return self.cur.fetchall()

	def create_con(self, db_path):
		self.con = self.connect_db(db_path)

	def create_table(self, table_name, attrs):
		sql = self.SQL['create'].format(table_name, attrs)
		self.cur_exec(sql)

	def insert(self, table_name, attrs, values):
		mark_str = ','.join(["?" for x in range(len(values))])
		sql = self.SQL['insert'].format(table_name, attrs, mark_str)
		self.cur_exec(sql, values)

	def update_table(self, table_name, *args):
		attrs, where_str = args
		sql = self.SQL['update'].format(table_name, attrs, where_str)
		self.cur_exec(sql)

	def select(self, table_name, values, where_str = None):
		sql = self.SQL['select'].format(values, table_name)
		if isinstance(where_str, str):
			sql = self.SQL['select where'].format(values, table_name, where_str)
		self.cur_exec(sql)
		return self.cur.fetchall()
	
	def delete_table(self, table_name):
		sql = self.SQL['drop'].format(table_name)
		self.cur_exec(sql)

	def connect_db(self, path):
		return sqlite3.connect(path)

	def cur_exec(self, *sql):
		self.cur = self.con.cursor()
		self.cur.execute(*sql)

	def commit(self):
		self.con.commit()

	def close(self):
		self.con.close()

# High level object for Agilis
# High level Database operations
class Omega(Agilis):
	# dbname {tablename:[attrs]}
	def init_db(self, db_name, table_dict=None):
		self.con = self.connect_db(db_name)
		if isinstance(table_dict, dict):
			for t, a in table_dict.items():
				self.create_table(t, a)
			self.commit()

	# {tablename:[value, where]}
	def update_tables(self, table_dict):
		for t, a in table_dict.items():
			self.update_table(t, a)

if __name__ == '__main__':
	pass