import subprocess as sp
import os
import json
import shutil
from re import sub,search,escape
from datetime import datetime
import requests
import sys
import fileinput

from ScanFolder import ScanFolder
from LinkFinder import LinkFinder
from SeriesFinder import *

# RANDOM FUNCTIONS --------------------------------------

def get_current_datetime():
	now = datetime.now()
	return '{:02d}.{:02d}.{} {:02d}:{:02d}'.format(now.day,now.month,now.year,now.hour,now.minute)

def read_config(cfg_path):
	with open(os.path.join(cfg_path,'config.json'), 'r') as cfg:
		cfg_json = json.loads(''.join([l for l in [sub('\t|\n','',l) for l in cfg.readlines()] if l and l[0] != '/']))
	return cfg_json['series_folder'],cfg_json['series'],cfg_json['log'],cfg_json['eurostreaming']

def check_site(url):
	if not search(r'eurostreaming',url): print('Site [{}] is NOT from EuroStreaming, please check it.'.format(url)); return False
	if requests.get(url).status_code != 200: print('Site [{}] is NOT working, please check it.'.format(url)); return False
	return True

def update_log(logline):
	n = 0
	for line in fileinput.input(os.path.join(SCRIPT_DIR,'script.log'), inplace = 1):
		match = search(r'(?:\[[0-9\.\s\:]+\]\s'+escape(log_line)+r')(?:\s\(([0-9]+)(?:\)))?',line)
		if match: n = int(match.group(1)) if match.group(1) else 1
		else: print(line,end='')
	last_line = '[{}] {} ({})\n'.format(get_current_datetime(),log_line,n+1) if n > 0 else '[{}] {}\n'.format(get_current_datetime(),log_line)
	with open(os.path.join(SCRIPT_DIR,'script.log'),'a') as f: f.write(last_line)

# COMMANDS ----------------------------------------------

def cmd_config():
	folder = SERIES_PATH if SERIES_PATH != 'put here yuor series folder path' else ''
	path = input('Series folder [{}]: '.format(folder))
	while not os.path.exists(path):
		path = input('Folder not exists. Retry: ')
	if path:
		for line in fileinput.input(os.path.join(SCRIPT_DIR,'config.json'), inplace = 1): 
			print(line.replace(SERIES_PATH,path),end='')
	print('Successful! New configuration saved correctly.')

def cmd_reset():
	with open(os.path.join(SCRIPT_DIR,'config.json'),'w+') as f: f.write('{\n\t// Eurostreaming site (may change over time)\n\t"eurostreaming": "https://eurostreaming.pet",\n\n\t// folder where you have (or want) the series\n\t"series_folder": "put here yuor series folder path",\n\n\t// log file and path\n\t// 1: YES, 0: NO\n\t"log": 1,\n\n\t// list of all the series you want to download\n\t// [NAME,LINK,LANGUAGE,MODE]\n\t// NAME: \n\t//  1. if you already have the folder: NAME should be the folder name\n\t//  2. if you don\'t have the folder yet: NAME will be the folder name\n\t// LINK: EuroStreming episodes link\n\t// LANGUAGE: ITA or ENG (it\'ll be SUB ITA)\n\t// MODE:\n\t//  1. FULL: download all the episode (available on EuroStreaming) missing in the folder\n\t//  2. NEW:  download only the episodes (available on EuroStreaming) after the newest in the folder [default]\n\t"series": [\n\t]\n}')

def cmd_list(): 
	series_list = '\n'.join(['{}. {} [{}] [{},{}]'.format(i+1,name,url,lang,mode) for i,(name,url,lang,mode) in enumerate(SERIES)])
	print(series_list) if series_list else print('No series found! Configure series.\n  1. Run script with --add\n  2. Modify "{}"'.format(os.path.join(SCRIPT_DIR,'config.json')))

def cmd_log():
	print(open(os.path.join(SCRIPT_DIR,'script.log')).read())

def cmd_auto_scan():
	already_config = [name for name,_,_,_ in SERIES]
	sugg_series =[cmd_add_auto(k,v,'scan') if v else (k,None) for k,v in {s:get_suggestion_list(EUROSTREAMING,s) for s in [se for se in [d for _,d,_ in os.walk(SERIES_PATH) if d][0] if se not in already_config]}.items()]
	print('\n## AUTOSCAN COMPLETE ##')
	series_toprint = ['{}. {} [{}] [{},{}]'.format(i+1,serie,site,lang,mode) if site else 'No series found for \'{}\'! Try with --add-auto.'.format(serie) for i,(serie,site,lang,mode) in enumerate(sorted(sugg_series,key=lambda x:(x[1] is None,x[1]))) if serie]
	if series_toprint: print('\n'.join(series_toprint))
	print('\n{} serie(s) added to download.'.format(len(series_toprint)))

def cmd_add_auto(name=None,series=None,add_mode='auto'):
	if not series:
		words_search = input('Serie name: ')
		series = get_suggestion_list(EUROSTREAMING,words_search)
	else:
		r = ''
		while r not in ['y','n','yes','no']:
			r = input('Do you want to add \'{}\'? [y|n]: '.format(name))
		if r[0] == 'n': series = None
	if series:
		if name: print('# List for \'{}\''.format(name))
		print_pretty_formatting(series)
		n = '0'
		while not n.isnumeric() or (n.isnumeric() and int(n) < 1 or int(n) > len(series)):
			n = input('Serie number: ')
		if name: print()
		result = [(series,url) for i,(series,url) in enumerate(series.items()) if i == int(n)-1][0]
		if add_mode == 'auto': new_name = input('Folder name [empty for \'{}\']: '.format(result[0]))
		new_name = new_name if new_name else result[0]
		if name: return cmd_add_man(name,result[1],'scan')
		else: cmd_add_man(new_name,result[1],add_mode)
	elif not name: print('No serie found with \'{}\'! Retry.'.format(words_search))
	else: return (None,None,None,None)

def cmd_add_man(name=None,url=None,add_mode='man'):
	if not name: name = input('Folder [Serie] name: ')
	while name.lower() in [name.lower() for name,_,_,_ in SERIES]:
		if add_mode == 'auto': print('ERROR: Serie already exists.'); return -1
		name = input('ERROR: Folder already exists.\nFolder [Serie] name: ')
	print()
	if not url: url = input('EuroStreaming url: ')
	while not check_site(url):
		url = input('EuroStreaming url: ')
	if url.lower() in [site.lower() for _,site,_,_ in SERIES]: print('WARNING: Site already exists.')
	if add_mode == 'man': print()
	lang = ''
	while lang.lower() not in ['eng','ita']:
		lang = input('Language [eng|ita]: ')
	print('\n- FULL: download all the episode missing in the folder\n- NEW:  download only the episodes after the newest in the folder')
	mode = ''
	while mode.lower() not in ['full','new']:
		mode = input('Mode [full|new]: ')
	# adding in config file
	new_serie = '\t\t'+str([name,url,lang.upper(),mode.upper()]).replace('\'','\"')
	for line in fileinput.input(os.path.join(SCRIPT_DIR,'config.json'), inplace = 1): 
			if search(r'\"]$',line): print(sub('\"]','\"],',line),end='')
			else: print(sub(r'^[\t]*\]',new_serie+'\n\t]',line),end='')
	if add_mode != 'scan':
		print('\nSuccessful! {} [{}] [{},{}] added correctly.'.format(name,url,lang,mode))
	else: print(); return name,url,lang,mode

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

def cmd_help(): print(	'--{0:<11}-{0[0]:<5}run configuration\n\n'
						'--{2:<11}-{2[0]:<5}add new tv serie [scan folder and add with automatic search]\n'
						'--{3:<11}-{7:<5}add new tv serie [automatic search]\n'
						'--{4:<11}-{8:<5}add new tv serie [manual]\n\n'
						'--{1:<11}-{1[0]:<5}series list\n'
						'--{5:<11}-{5[0]:<5}remove tv serie\n\n'
						'--{9:<11}-{10:<5}reset a corrupted or missing config file\n'
						'--{11:<11}-{12:<5}show log file\n'
						'--{6:<11}-{6[0]:<5}show this message'
						.format('config','list','scan','add-auto','add-man','remove','help','aa','am','reset','rs','log','lg'))

# MAIN SCRIPT -------------------------------------------

if __name__ == '__main__':

	# grab info from config
	SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
	try: SERIES_PATH,SERIES,LOG,EUROSTREAMING = read_config(SCRIPT_DIR)
	except KeyError: print('config file corrupted, please check your file or run --reset'); exit()
	except json.decoder.JSONDecodeError: print('config file corrupted, please check your file or run --reset'); exit()
	except FileNotFoundError: print('config file not found, recreating...'); cmd_reset(); exit()

	# commands
	commands = {'config':cmd_config,'help':cmd_help,'scan':cmd_auto_scan,'add-man':cmd_add_man,'add-auto':cmd_add_auto,'list':cmd_list,'remove':cmd_remove,'reset':cmd_reset,'log':cmd_log}
	alias_commands = {'c':cmd_config,'h':cmd_help,'am':cmd_add_man,'aa':cmd_add_auto,'s':cmd_auto_scan,'l':cmd_list,'r':cmd_remove,'rs':cmd_reset,'lg':cmd_log}
	try:
		if search(r'^[\-]{2}',sys.argv[1]) and sys.argv[1][2:] in commands: commands[sys.argv[1][2:]]()
		elif search(r'^[\-]{1}[a-z]+',sys.argv[1]) and sys.argv[1][1:] in alias_commands: alias_commands[sys.argv[1][1:]]()
		else: print('USAGE: europlexo [--option]'); cmd_help()
	except IndexError:

		# check folders
		if not SERIES_PATH or not os.path.exists(SERIES_PATH): print('Series folder not found!\nConfigure your folder path with --config'); exit()
		if not SERIES: print('No series found!\nConfigure series with one of the add command.\nFind out more with --help'); exit()
		if not all([check_site(site) for _,site,_,_ in SERIES]): exit()

		# set tmp and log files
		TMP_PATH = os.path.join(SCRIPT_DIR,'tmp')
		if not os.path.exists(TMP_PATH): os.mkdir(TMP_PATH)
		error_log_path = os.path.join(TMP_PATH,'error.log')
		script_log_path = os.path.join(SCRIPT_DIR,'script.log')
		if not os.path.exists(script_log_path): open(script_log_path, 'a').close()
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
							log_line = 'Downloaded episode of {} [{}×{}]'.format(name,season,episode)
							if LOG: update_log(log_line), print(log_line)
							break
					if search(r'ERROR',READ_ERROR_LOG()):
						log_line = 'No link working for {} [{}×{}]'.format(name,season,episode)
						if LOG: update_log(log_line), print(log_line)
					else: 
						# moving from tmp to series folder
						tmp_file = [f for _,_,files in os.walk(TMP_PATH) for f in files if search(name.replace(' ','_'),f)][0]
						tmp_file_path = os.path.join(TMP_PATH,tmp_file)
						season_path = sf.get_abspath_season(season)
						if not os.path.exists(season_path): os.mkdir(season_path)
						destination_path = os.path.join(season_path,tmp_file)
						shutil.move(tmp_file_path, destination_path)
				except ValueError:
					log_line = 'No link found for {} [{}×{}]'.format(name,season,episode)
					if LOG: update_log(log_line), print(log_line)
				print()
		
		# deleting tmp folder
		shutil.rmtree(TMP_PATH)