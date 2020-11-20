# 
# _________________ Built-in Dependencies _________________
# 
import os, sqlite3, shutil, random, random, re, time, threading, sys, json, secrets
from requests import get
from os.path import join, basename, dirname
from queue import Queue

# 
# _________________ Decorators _________________
# 
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

# 
# _________________ Utility Class
# 
class Nexus:
	# 
	# _________________ String Operations _________________
	# 
	@staticmethod
	def sleep(sec):
		time.sleep(sec)

	@staticmethod
	def gen_hex(x):
		return secrets.token_hex(x).upper()

	@staticmethod
	def sep_url(url):
		return os.path.normpath(url).split(os.sep)

	@staticmethod
	def date_(res = ['date', 'mtime', 'mdtime'], frmt_str = None):
		date_str = r'%d-%m-%Y'
		mtime_str = r'%H_%M_%S'
		if 'date' in res: return time.strftime(date_str)
		elif 'mtime' in res: return  time.strftime(mtime_str)
		elif 'mdtime' in res: return  time.strftime(f'{date_str} {mtime_str}')
		elif isinstance(frmt_str, str): return time.strftime(frmt_str)

	# 
	# _________________ Generators _________________
	# 
	def check_dir_exist(self, dirname = None):
		if isinstance(dirname, str):
			self.make_dirs(dirname)
		elif isinstance(dirname, list):
			for name in dirname: self.make_dirs(name)

	def make_dirs(self, path):
		try:
			if not os.path.isdir(path): os.makedirs(path)
		except:
			print(f'Not a valid path {path}')


	# 
	# _________________ File Operations _________________
	# 
	@staticmethod
	def json_handle(filename = None, data = None, open_opt = None):
		if data and isinstance(filename, str):
			with open(filename, 'w') as j: json.dump(data, j, indent='\t')
		elif not data and isinstance(filename, str) and os.path.isfile(filename):
			with open(filename, 'r') as j: return json.load(j)
		elif data and isinstance(filename, str) and isinstance(open_opt, str):
			with open(filename, 'o') as j: json_dump(data, j, indent='\t')

	@staticmethod
	def file_handle(filename = None, opt = None, data = None, reverse = False):
		verify_name = isinstance(filename, str)
		if verify_name and 'w' in opt:
			with open(filename, 'w') as f: f.write(data)
		elif verify_name and 'r' in opt:
			with open(filename, 'r') as f: return f.read()
		elif verify_name and 'rm' in opt:
			with open(filename, 'r') as f: data = f.read()
			return sorted(list(set(data.split('\n'))), reverse=reverse)
		elif verify_name and 'wb' in opt:
			with open(filename, 'wb') as f: f.write(data)
		elif verify_name and 'rb' in opt:
			with open(filename, 'rb') as f: return f.read()

	@staticmethod
	def walk_path(path = None, method = ['files', 'folders', 'all'], exts = None):
		if isinstance(exts, list):
			return [join(path, d) for d in os.listdir(path) if os.path.splitext(d)[1][1:] in exts]
		elif isinstance(method, str) and 'all' in method:
			return [join(path, d) for d in os.listdir(path)]
		elif isinstance(method, str) and 'files' in method:
			return [join(path, d) for d in next(os.walk(path))[2]]
		elif isinstance(method, str) and 'folders' in method:
			return [join(path, d) for d in next(os.walk(path))[1]]

	# 
	# _________________ Generators _________________
	# 
	@staticmethod
	def replace_all(text, re_):
		for i, j in re_.items():
			text = text.replace(i, j)
		return text

	@staticmethod
	def find_in(needle, haystack):
		for hay in haystack:
			if needle in hay: return hay
		
	# 
	# _________________ Requests _________________
	# 
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


	# 
	# _________________ Threading, Datastructs _________________
	# 
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

	def schema_init(self, root_folds=None):
		self.DATA_STORE = dict(
			[
				( 'src', join(os.getcwd(), 'src') ),
				( 'folders', dict() ),
				( 'data', {'imgs':list()} )
			]
		)

		if isinstance(root_folds, list):
			print('no root folds found')
			return self.DATA_STORE
		else:
			# declare folders in root
			root_folds = ['archive', 'json', 'db']

			# build folders
			root = self.DATA_STORE.get('src')
			folders = {k:join(root, k) for k in root_folds}
			self.DATA_STORE.get('folders').update(folders)
			for d in folders.values(): self.make_dirs(d)

	def img_dl_threader(self, data):
		url, dest_filename = data
		if basename(dest_filename) not in self.walk_path(dirname(dest_filename)):
			try: self.dl_file(url, dest_filename)
			except: print(f'Error with {url}')
		else:
			print(f'{url} already present')



# 
# _________________ SQL Utility
# 
class Arch:
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

	def con_create(self, db_path):
		self.con = self.connect_db(db_path)

	def table_create(self, table_name, attrs):
		sql = self.SQL['create'].format(table_name, attrs)
		self.cur_exec(sql)

	def table_insert(self, table_name, attrs, values):
		mark_str = ','.join(["?" for x in range(len(values))])
		sql = self.SQL['insert'].format(table_name, attrs, mark_str)
		self.cur_exec(sql, values)

	def table_update(self, table_name, *args):
		attrs, where_str = args
		sql = self.SQL['update'].format(table_name, attrs, where_str)
		self.cur_exec(sql)

	def table_select(self, table_name, values, where_str = None):
		sql = self.SQL['select'].format(values, table_name)
		if isinstance(where_str, str):
			sql = self.SQL['select where'].format(values, table_name, where_str)
		self.cur_exec(sql)
		return self.cur.fetchall()
	
	def table_delete(self, table_name):
		sql = self.SQL['drop'].format(table_name)
		self.cur_exec(sql)

	def connect_db(self, path):
		return sqlite3.connect(path)

	def cur_exec(self, *sql):
		self.cur = self.con.cursor()
		self.cur.execute(*sql)

	def sql_commit(self):
		self.con.commit()

	def sql_close(self):
		self.con.close()


# High level object for Arch
# High level Database operations
class Omega(Arch):
	# dbname {tablename:attrs}
	def init_db(self, db_name, table_dict=None):
		self.con = self.connect_db(db_name)
		if isinstance(table_dict, dict):
			for t, a in table_dict.items():
				self.table_create(t, a)
			self.sql_commit()
		elif not isinstance(table_dict, dict):
			self.con = self.connect_db(db_name)
			return None

	# {tablename:[value, where]}
	def update_tables(self, table_dict):
		for t, a in table_dict.items():
			self.table_update(t, a)


if __name__ == '__main__':
	pass