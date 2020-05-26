import subprocess as sp
import os
import json
import shutil
from re import sub,search
from datetime import datetime
import requests
import sys
import fileinput

from ScanFolder import ScanFolder
from LinkFinder import LinkFinder

# RANDOM FUNCTIONS --------------------------------------

def get_current_datetime():
	now = datetime.now()
	return '{:02d}.{:02d}.{} {:02d}:{:02d}'.format(now.day,now.month,now.year,now.hour,now.minute)

def read_config(cfg_path):
	with open(os.path.join(cfg_path,'config.json'), 'r') as cfg:
		cfg_json = json.loads(''.join([l for l in [sub('\t|\n','',l) for l in cfg.readlines()] if l and l[0] != '/']))
	return cfg_json['series_folder'],cfg_json['series'],cfg_json['log']

def check_site(url):
	if not search(r'eurostreaming',url): print('Site [{}] is NOT from EuroStreaming, please check it.'.format(url)); return False
	if requests.get(url).status_code != 200: print('Site [{}] is NOT working, please check it.'.format(url)); return False
	return True

# COMMANDS ----------------------------------------------

def cmd_config():
	folder = SERIES_PATH if SERIES_PATH != 'put here yuor series folder path' else ''
	path = input('Series folder [{}]: '.format(folder))
	if path:
		for line in fileinput.input(os.path.join(SCRIPT_DIR,'config.json'), inplace = 1): 
			print(line.replace(SERIES_PATH,path),end='')
	print('Successful! New configuration saved correctly.')


def cmd_list(): 
	series_list = '\n'.join(['{}. {} [{}] [{},{}]'.format(i+1,name,url,lang,mode) for i,(name,url,lang,mode) in enumerate(SERIES)])
	print(series_list) if series_list else print('No series found! Configure series.\n  1. Run script with --add\n  2. Modify "{}"'.format(os.path.join(SCRIPT_DIR,'config.json')))

def cmd_add():
	name = input('Folder [Serie] name: ')
	while name in [name for name,_,_,_ in SERIES]:
		name = input('ERROR: Folder already exists.\nFolder [Serie] name: ')
	print()
	url = input('EuroStreaming url: ')
	while not check_site(url):
		url = input('EuroStreaming url: ')
	if url in [site for _,site,_,_ in SERIES]: print('WARNING: Site already exists.')
	print()
	lang = ''
	while lang.lower() not in ['eng','ita']:
		lang = input('Language [eng|ita]: ')
	print('\n- FULL: download all the episode missing in the folder\n- NEW:  download only the episodes after the newest in the folder')
	mode = ''
	while mode.lower() not in ['full','new']:
		mode = input('Mode [full|new]: ')
	# adding in config file
	else:
		new_serie = '\t\t'+str([name,url,lang.upper(),mode.upper()]).replace('\'','\"')
		for line in fileinput.input(os.path.join(SCRIPT_DIR,'config.json'), inplace = 1): 
				if search(r'\"]$',line): print(sub('\"]','\"],',line),end='')
				else: print(sub(r'^[\t]*\]',new_serie+'\n\t]',line),end='')
	print('Successful! {} [{}] [{},{}] added correctly.'.format(name,url,lang,mode))

def cmd_remove():
	cmd_list(); print()
	n = int(input('Serie number to remove: '))
	while n < 1 or n > len(SERIES): n = int(input('ERROR! Number must be between 1 and {}: '.format(len(SERIES))))
	name = SERIES[n-1][0]
	i = 0
	for line in fileinput.input(os.path.join(SCRIPT_DIR,'config.json'), inplace = 1):
		if search(r'\"]\,?$',line):
			i += 1
			if n == i+1 and n+1 > len(SERIES): print(sub(r'\]\,',']',line),end='')
			elif n != i: print(line,end='')
		else: print(line,end='')
	print('Successful! {} removed correctly.'.format(name))

def cmd_help(): print('--{0:<9}-{0[0]:<4}run configuration\n--{1:<9}-{1[0]:<4}series list\n--{2:<9}-{2[0]:<4}add new tv serie\n--{3:<9}-{3[0]:<4}remove tv serie\n--{4:<9}-{4[0]:<4}show commands'.format('config','list','add','remove','help'))

# MAIN SCRIPT -------------------------------------------

if __name__ == '__main__':

	# grab info from config
	SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
	try: SERIES_PATH,SERIES,LOG = read_config(SCRIPT_DIR)
	except KeyError: print('Config file corrupted, please download everything again!'); exit()

	# commands
	commands = {'config':cmd_config,'help':cmd_help,'add':cmd_add,'list':cmd_list,'remove':cmd_remove}
	alias_commands = {'c':cmd_config,'h':cmd_help,'a':cmd_add,'l':cmd_list,'r':cmd_remove}
	try:
		if search(r'^[\-]{2}',sys.argv[1]) and sys.argv[1][2:] in commands: commands[sys.argv[1][2:]]()
		elif search(r'^[\-]{1}[a-z]+',sys.argv[1]) and sys.argv[1][1:] in alias_commands: alias_commands[sys.argv[1][1:]]()
		else: print('Command not found.'); cmd_help()
	except IndexError:

		# check folders
		if not SERIES_PATH or not os.path.exists(SERIES_PATH): print('Series folder not found! Configure folder path again.\n  1. Run script with --config\n  2. Modify "{}"'.format(os.path.join(SCRIPT_DIR,'config.json'))); exit()
		if not SERIES: print('No series found! Configure series.\n  1. Run script with --add\n  2. Modify "{}"'.format(os.path.join(SCRIPT_DIR,'config.json'))); exit()
		if not all([check_site(site) for _,site,_,_ in SERIES]): exit()

		# set tmp and log files
		TMP_PATH = os.path.join(SCRIPT_DIR,'tmp')
		if not os.path.exists(TMP_PATH): os.mkdir(TMP_PATH)
		error_log_path = os.path.join(TMP_PATH,'error.log')
		script_log_path = os.path.join(SCRIPT_DIR,'script.log')
		ERROR_LOG = open(error_log_path,'w+')
		READ_ERROR_LOG = lambda : open(error_log_path).read()
		
		# grab info from the series folder
		sf = ScanFolder(SERIES_PATH)

		# run the script for every series
		for name,link,language,mode in SERIES:
			mode = mode if mode in ['NEW','FULL'] else 'NEW'
			language = language.lower() == 'ENG'.lower()

			# scan the folder
			sf.scan_serie(name,mode)

			# grab episodes missing
			lf = LinkFinder(link,language)
			eps = sf.episode_missing(lf.info)
			
			# download every episodes
			for season,episode in eps:
				file_name = '{0:02d}. {2}_{1}x{0}.{3}'.format(episode,season,name.replace(' ','_'),'%(ext)s')
				try:
					_,direct_links = lf.get_direct_links(season,episode)
					print('Downloading {} [{}×{}]'.format(name,season,episode))
					print('Link(s) found:')
					print('\n'.join(['{:>3}. {}'.format(i+1,l) for i,l in enumerate(direct_links)]))
					print()
					for l in direct_links:
						sp.run(['youtube-dl','--no-check-certificate','-o',os.path.join(TMP_PATH,file_name),l], stderr=ERROR_LOG)
						if not search(r'ERROR',READ_ERROR_LOG()):
							log_line = '[{}] Downloaded episode of {} [{}×{}].'.format(get_current_datetime(),name,season,episode)
							if LOG:
								with open(script_log_path,'a+') as f: f.write(log_line+'\n')
							print(log_line)
							break
					if search(r'ERROR',READ_ERROR_LOG()):
						log_line = '[{}] no links working for {} [{}×{}].'.format(get_current_datetime(),name,season,episode)
						if LOG:
							with open(script_log_path,'a+') as f: f.write(log_line+'\n')
							print(log_line)
					else: 
						# moving from tmp to series folder
						tmp_file = [f for _,_,files in os.walk(TMP_PATH) for f in files if search(name.replace(' ','_'),f)][0]
						tmp_file_path = os.path.join(TMP_PATH,tmp_file)
						season_path = sf.get_abspath_season(season)
						if not os.path.exists(season_path): os.mkdir(season_path)
						destination_path = os.path.join(season_path,tmp_file)
						shutil.move(tmp_file_path, destination_path)
				except ValueError:
					log_line = '[{}] No link found for {} [{}×{}].'.format(get_current_datetime(),name,season,episode)
					if LOG:
						with open(script_log_path,'a+') as f: f.write(log_line+'\n')
						print(log_line)
				print()
		
		# deleting tmp folder
		shutil.rmtree(TMP_PATH)