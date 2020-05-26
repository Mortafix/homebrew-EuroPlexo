from re import search,sub
import os

class ScanFolder():
	def __init__(self,path):
		self.path = os.path.abspath(path)

	def __str__(self):
		try:
			info_pretty_printing = '\n'.join(['Season {}: {}'.format(s,e) for s,e in self.folder_info.items()])
			return 'Scan PATH: {}\nSerie: {}\n-- Info --\n{}'.format(self.path,self.serie_folder_name,info_pretty_printing)
		except AttributeError: return 'Scan PATH: {}'.format(self.path)

	def _get_season_folder_name(self):
		'''Template for season folder name'''
		return sub('[0-9]{1,2}','##',next(os.walk('/'.join([self.path,self.serie_folder_name])))[1][0])

	def scan_serie(self,serie_folder_name,mode):
		'''Scan a specific serie | get all episodes'''
		self.mode = mode
		self.serie_folder_name = serie_folder_name
		info = dict()
		if os.path.isdir('/'.join([self.path,serie_folder_name])):
			self.season_folder_name = self._get_season_folder_name()
			for i,(_,dirs,files) in enumerate(os.walk('/'.join([self.path,serie_folder_name]))):
				if i == 0: seasons = [int(m.group(1)) if m else 0 for m in [search(r'([0-9]{1,2})',d) for d in dirs]]
				elif seasons[i-1] != 0: info[seasons[i-1]] = sorted(set([int(m.group(1)) for m in [search(r'([0-9]{1,3})(?:\.)',f) for f in files] if m]))
		else:
			os.mkdir('/'.join([self.path,serie_folder_name]))
			self.season_folder_name = 'Stagione ##'
			os.mkdir(self.get_abspath_season(1))
		self.folder_info = {k: v for k, v in sorted(info.items())} if info else info

	def episode_missing(self,serie_site_info):
		'''Get missing episodes base on mode and already downloaded'''
		try:
			eps = [(se,ep) for se in serie_site_info.keys() for ep in range(1,serie_site_info[se]+1) if se not in self.folder_info or (se in self.folder_info and ep not in self.folder_info[se])]
			if self.mode == 'NEW': eps = [(se,ep) for se,ep in eps if not self.folder_info or se > max(self.folder_info) or (se == max(self.folder_info) and (not self.folder_info[se] or ep > max(self.folder_info[se])))]
			return eps
		except AttributeError: raise AttributeError('You need to run scan_serie() first.')

	def get_abspath_season(self,season_number):
		'''Get the absolute path for a specific season'''
		return '/'.join([self.path,self.serie_folder_name,sub('##',str(season_number),self.season_folder_name)])

if __name__ == '__main__':
	PATH = 'test'
	site_info = {1:15,2:16,3:25,4:10,5:14,6:17,7:5}
	sf = ScanFolder(PATH)
	sf.scan_serie('The Flash','NEW')
	eps = sf.episode_missing(site_info)
	print(eps)
	print(sf)