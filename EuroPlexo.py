#!/usr/bin/env python3
# Author: Moris Doratiotto

import subprocess as sp
import os
import json
import shutil
from re import sub,search,escape,match
from datetime import datetime
import requests
from requests.exceptions import ConnectionError, InvalidURL
import sys
import fileinput
from emoji import emojize

from ScanFolder import ScanFolder
from LinkFinder import LinkFinder
from SeriesFinder import *

# RANDOM FUNCTIONS --------------------------------------

def int_to_hr_size(size):
	return '{:.0f} MB'.format(size) if size < 1000 else '{:.2f} GB'.format(size / 1000)

def get_current_datetime():
	now = datetime.now()
	return '{:02d}.{:02d}.{} {:02d}:{:02d}'.format(now.day,now.month,now.year,now.hour,now.minute)

def read_config(cfg_path):
	with open(os.path.join(cfg_path,'config.json'), 'r') as cfg:
		cfg_json = json.loads(''.join([l for l in [sub('\t|\n','',l) for l in cfg.readlines()] if l and l[0] != '/']))
	return cfg_json['series_folder'],cfg_json['series'],cfg_json['log'],cfg_json['eurostreaming'],cfg_json['telegram_bot_token'],cfg_json['telegram_chat_id']

def autoget_eurostreaming_site():
	try:
		site = search(r'(?:<title>site:)(.+)(?:\s-\sCerca)',requests.get('https://eurostreaming.top').text).group(1)
		return site if search('http',site) else 'https://{}'.format(site)
	except ConnectionError: return 'https://eurostreaming.cloud'

def em(emoji_string):
	return emojize(':'+emoji_string+':',use_aliases=True)

def check_site(url):
	try:
		if not search(r'eurostreaming',url): print('Site [{}] is NOT from EuroStreaming, please check it.'.format(url)); return False
		if requests.get(url).status_code != 200: print('Site [{}] is NOT working, please check it.'.format(url)); return False
	except (ConnectionError, InvalidURL): print('Site [{}] is NOT working, please check it.'.format(url)); return False
	return True

def update_log(logline):
	if BOT_TOKEN: send_telegram_log(logline)
	n = 0
	for line in fileinput.input(os.path.join(SCRIPT_DIR,'script.log'), inplace = 1):
		match = search(r'(?:\[[0-9\.\s\:]+\]\s'+escape(logline)+r')(?:\s\{([0-9]+)(?:\}))?',line)
		if match: n = int(match.group(1)) if match.group(1) else 1
		else: print(line,end='')
	last_line = '[{}] {} {{{}}}\n'.format(get_current_datetime(),logline,n+1) if n > 0 else '[{}] {}\n'.format(get_current_datetime(),logline)
	with open(os.path.join(SCRIPT_DIR,'script.log'),'a') as f: f.write(last_line)

def send_telegram_log(logline):
	datetime = get_current_datetime().split()
	info = search(r'(?:episode of |found for )(.+)\s\[(\d\d?×\d\d?)\]\s(?:\((.+)\))?',logline)
	serie = info.group(1)
	episode = info.group(2)
	size = '{} {}'.format(em('bulb'),info.group(3)) if info.group(3) else None
	size = sub('->',em('arrow_forward'),size) if size else ''
	size = sub(r'([\d\.]+)',r'*\1*',size)
	if not size: what = '{0} No link found {0}'.format(em('no_entry'))
	elif search(r'B\s',size): what = '{0} Redownloaded episode {0}'.format(em('eight_pointed_black_star'))
	else: what = '{0} Downloaded episode {0}'.format(em('white_check_mark'))
	msg = '{4}\n\n{0} {1}\n{2} {3}\n\n{5} *{6}*\n{7} Episode *{8}*\n{9}'.format(em('date'),datetime[0],em('clock5'),datetime[1],what,em('clapper'),serie.upper(),em('cyclone'),episode,size)
	params = {"chat_id":TELEGRAM_ID,"text":msg,"parse_mode": "Markdown"}
	requests.get("https://api.telegram.org/bot{}/sendMessage".format(BOT_TOKEN),params=params)

def add_http(url):
	return "http://"+url if not match(r'http',url) else url

def get_size_last_file(series_folder_path,serie_name,season,episode):
	path = os.path.join(series_folder_path,serie_name,'Stagione {}'.format(season))
	last_file = [file for file in list(os.walk(path))[0][2] if match(r'0?'+str(episode),file)][0]
	try: return last_file,os.path.getsize(os.path.join(path,last_file)) / 1000**2
	except IndexError: return '',0

# COMMANDS ----------------------------------------------

def cmd_config(*args):
	folder = SERIES_PATH if SERIES_PATH != 'put here yuor series folder path' else ''
	path = input('Series folder [{}]: '.format(folder))
	while not os.path.exists(path):
		path = input('Folder not exists. Retry: ')
	if path:
		for line in fileinput.input(os.path.join(SCRIPT_DIR,'config.json'), inplace = 1): 
			print(line.replace(SERIES_PATH,path),end='')
	print('Successful! New configuration saved correctly.')

def cmd_reset(*args):
	with open(os.path.join(SCRIPT_DIR,'config.json'),'w+') as f: f.write('{\n\t// manul Eurostreaming site(may change over time, keep empty for auto retrieve)\n\t"eurostreaming": "",\n\n\t// folder where you have (or want) the series\n\t"series_folder": "put here yuor series folder path",\n\n\t// log file and path\n\t// 1: YES, 0: NO\n\t"log": 1,\n\n\t// list of all the series you want to download\n\t// [NAME,LINK,LANGUAGE,MODE]\n\t// NAME: \n\t//  1. if you already have the folder: NAME should be the folder name\n\t//  2. if you don\'t have the folder yet: NAME will be the folder name\n\t// LINK: EuroStreming episodes link\n\t// LANGUAGE: ITA or ENG (it\'ll be SUB ITA)\n\t// MODE:\n\t//  1. FULL: download all the episode (available on EuroStreaming) missing in the folder\n\t//  2. NEW:  download only the episodes (available on EuroStreaming) after the newest in the folder [default]\n\t"series": [\n\t],\n\n\t// Telegram bot token and your Telegram chat ID to receive log messages\n\t"telegram_bot_token": "",\n\t"telegram_chat_id": ""\n}')
	print('Config file resetted.')

def cmd_list(*args): 
	series_list = '\n'.join(['{}. {} [{}] [{},{}]'.format(i+1,name,os.path.join(EUROSTREAMING,url),lang,mode) for i,(name,url,lang,mode) in enumerate(SERIES)])
	print(series_list) if series_list else print('No series found!\nRun -aa (or --add-auto)')

def cmd_log(*args):
	script_path = os.path.join(SCRIPT_DIR,'script.log')
	if not os.path.exists(script_path): open(script_path, 'a').close()
	print(open(script_path).read()[:-1])

def cmd_test_telegram(*args):
	send_telegram_log('Test message from Europlexo')

def cmd_auto_scan(*args):
	already_config = [name for name,_,_,_ in SERIES]
	sugg_series =[cmd_add_auto(name=k,series=v,add_mode='scan') if v else (k,None) for k,v in {s:get_suggestion_list(EUROSTREAMING,s) for s in [se for se in [d for _,d,_ in os.walk(SERIES_PATH) if d][0] if se not in already_config]}.items()]
	print('\n## AUTOSCAN COMPLETE ##')
	series_toprint = ['{}. {} [{}] [{},{}]'.format(i+1,serie,site,lang,mode) if site else 'No series found for \'{}\'! Try with --add-auto.'.format(serie) for i,(serie,site,lang,mode) in enumerate(sorted(sugg_series,key=lambda x:(x[1] is None,x[1]))) if serie]
	if series_toprint: print('\n'.join(series_toprint))
	print('\n{} serie(s) added to download.'.format(len(series_toprint)))

def cmd_add_auto(*args,name=None,series=None,add_mode='auto'):
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
		if add_mode == 'auto':
			new_name = input('Folder name [empty for \'{}\']: '.format(result[0]))
			new_name = new_name if new_name else result[0]
			cmd_add_man(name=new_name,url=result[1],add_mode=add_mode)
		else: return cmd_add_man(name=name,url=result[1],add_mode='scan') 
	elif not name: print('No serie found with \'{}\'! Retry.'.format(words_search))
	else: return (None,None,None,None)

def cmd_add_man(*args,name=None,url=None,add_mode='man'):
	if not name: name = input('Folder [Serie] name: ')
	while name.lower() in [name.lower() for name,_,_,_ in SERIES]:
		if add_mode == 'auto': print('ERROR: Serie already exists.'); return -1
		name = input('ERROR: Folder already exists.\nFolder [Serie] name: ')
	print()
	if not url: url = add_http(input('EuroStreaming url: '))
	while not check_site(url):
		url = add_http(input('EuroStreaming url: '))
	original_url = url
	url = search(r'(?:.+\/)(.+)(?:\/?)',url).group(1)
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
		print('\nSuccessful! {} [{}] [{},{}] added correctly.'.format(name,original_url,lang,mode))
	else: print(); return name,url,lang,mode

def cmd_remove(*args):
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

def cmd_link(*args):
	if not SERIES: cmd_list(); return 0
	if not args[0]: print('USAGE: -gl (or --get-link) [series-number-from-your-list]\nRun -l (or --list) to see series numbers.'); return 0
	try:
		name,url,sub,_ = SERIES[int(args[0][0])-1]
		url = os.path.join(EUROSTREAMING,url)
		sub = sub == 'ENG'
		lk = LinkFinder(url,sub)
		(season,episode),links = lk.get_direct_links()
		print('Link(s) for {} [{}×{}]\n\n{}'.format(name,season,episode,'\n'.join(['({1}) {0}'.format(l,int_to_hr_size(s)) for l,s in links])))
	except ValueError: print('USAGE: -gl (or --get-link) [series-number-from-your-list]\nRun -l (or --list) to see series numbers.')
	except IndexError: print('Series number ({}) out of list!\nShould be between 1 and {}.'.format(int(args[0][0]),len(SERIES)))
	finally: return 0

def cmd_redown(*args):
	if not SERIES: cmd_list(); return 0
	if not args[0]: print('USAGE: -re (or --redownload) [series-number-from-your-list]\nRun -l (or --list) to see series numbers.'); return 0
	try:
		name,url,sub,mode = SERIES[int(args[0][0])-1]
		url = os.path.join(EUROSTREAMING,url)
		sub = sub == 'ENG'
		sf = ScanFolder(SERIES_PATH)
		sf.scan_serie(name,mode)
		lk = LinkFinder(url,sub=sub)
		(season,episode),links = lk.get_direct_links()
		last_episode_file_name,last_episode_file_size = get_size_last_file(SERIES_PATH,name,season,episode)
		season_path = sf.get_abspath_season(season)
		print('{} [{}×{}]\n\n({}) {}\n{}'.format(name,season,episode,int_to_hr_size(last_episode_file_size),last_episode_file_name,'\n'.join(['({1}) {0}'.format(l,int_to_hr_size(s)) for l,s in links])))
		if max([s for l,s in links]) > last_episode_file_size + 25:
			print('\nRedownloading {} [{}×{}] ({} -> {})\n'.format(name,season,episode,int_to_hr_size(last_episode_file_size),int_to_hr_size(links[0][1])))
			download_episode(name,season,episode,links,redown=last_episode_file_size,season_path=season_path) # redownloading
		else: print('\nNothing to redownload.\n') 
	except ValueError: print('USAGE: -re (or --redownload [series-number-from-your-list]\nRun -l (or --list) to see series numbers.')
	except IndexError: print('Series number ({}) out of list!\nShould be between 1 and {}.'.format(int(args[0][0]),len(SERIES)))
	finally: return 0

def cmd_redown_all(*args):
	if not SERIES: cmd_list(); return 0
	for i in range(1,len(SERIES)+1): cmd_redown([i])

def cmd_help(*args): print(	'--{0:<16}-{0[0]:<5}run configuration\n\n'
						'--{2:<16}-{2[0]:<5}add new tv serie [scan folder and add with automatic search]\n'
						'--{3:<16}-{7:<5}add new tv serie [automatic search]\n'
						'--{4:<16}-{8:<5}add new tv serie [manual]\n'
						'--{1:<16}-{1[0]:<5}series list\n'
						'--{5:<16}-{5[0]:<5}remove tv serie\n\n'
						'--{13:<16}-{14:<5}get links last episode for a serie\n'
						'--{15:<16}-{16:<5}redownload last episode for a serie (if higher quality)\n'
						'--{17:<16}-{18:<5}redownload last episode for all series (if higher quality)\n\n'
						'--{9:<16}-{10:<5}reset a corrupted or missing config file\n'
						'--{11:<16}-{12:<5}show log file\n'
						'--{19:<16}-{19[0]:<5}test Telegram log message\n'
						'--{6:<16}-{6[0]:<5}show this message'
						.format('config','list','scan','add-auto','add-man','remove','help','aa','am','reset','rs','log','lg','get-last','gl','redl','re','redl-all','ra','test-telegram'))

# DOWNLOADING FUNCTION ----------------------------------

def download_episode(serie,season,episode,direct_links,redown=None,season_path=None):
	file_name = '{0:02d}. {2}_{1}x{0}.{3}'.format(episode,season,serie.replace(' ','_'),'%(ext)s')
	for l,s in direct_links:
		sp.run(['youtube-dl','--no-check-certificate','-o',os.path.join(TMP_PATH,file_name),l], stderr=ERROR_LOG)
		if not search(r'ERROR',READ_ERROR_LOG()):
			log_line = 'Downloaded episode of {} [{}×{}] ({})'.format(serie,season,episode,int_to_hr_size(s)) if not redown else 'Redownloaded episode of {} [{}×{}] ({} -> {})'.format(serie,season,episode,int_to_hr_size(redown),int_to_hr_size(s))
			if LOG: update_log(log_line), print(log_line)
			break
	if search(r'ERROR',READ_ERROR_LOG()):
		log_line = 'No link working for {} [{}×{}]'.format(serie,season,episode)
		if LOG: update_log(log_line), print(log_line)
	# moving from tmp to series folder
	else: 
		season_path = sf.get_abspath_season(season) if not season_path else season_path
		if redown: os.remove(os.path.join(season_path,[f for _,_,files in os.walk(season_path) for f in files if search(r'{}\.\s'.format(episode),f)][0])) # delete redowloaded episode
		tmp_file = [f for _,_,files in os.walk(TMP_PATH) for f in files if search(escape(serie.replace(' ','_')),f)][0]
		tmp_file_path = os.path.join(TMP_PATH,tmp_file)
		if not os.path.exists(season_path): os.mkdir(season_path)
		destination_path = os.path.join(season_path,tmp_file)
		shutil.move(tmp_file_path, destination_path)

# MAIN SCRIPT -------------------------------------------

if __name__ == '__main__':

	try:
			
		# grab info from config
		SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
		try: SERIES_PATH,SERIES,LOG,EUROSTREAMING,BOT_TOKEN,TELEGRAM_ID = read_config(SCRIPT_DIR)
		except KeyError: print('ERROR: config file corrupted, please check your file or run --reset'); exit()
		except json.decoder.JSONDecodeError: print('ERROR: config file corrupted, please check your file or run --reset'); exit()
		except FileNotFoundError: print('WARNING: config file not found, recreating and running the --config.'); cmd_reset(); SERIES_PATH,SERIES,LOG,EUROSTREAMING,BOT_TOKEN,TELEGRAM_ID = read_config(SCRIPT_DIR); cmd_config(); exit()

		# check site
		if not EUROSTREAMING: EUROSTREAMING = autoget_eurostreaming_site()
		if not EUROSTREAMING: print('I can\'t retrieve EuroStreaing site.\nPlease wait a few minutes or insert manually.'); exit() 

		# set tmp and log files
		TMP_PATH = os.path.join(SCRIPT_DIR,'tmp')
		if not os.path.exists(TMP_PATH): os.mkdir(TMP_PATH)
		error_log_path = os.path.join(TMP_PATH,'error.log')
		script_log_path = os.path.join(SCRIPT_DIR,'script.log')
		if not os.path.exists(script_log_path): open(script_log_path, 'a').close()
		ERROR_LOG = open(error_log_path,'w+')
		READ_ERROR_LOG = lambda : open(error_log_path).read()

		# commands
		commands = {'config':cmd_config,'help':cmd_help,'scan':cmd_auto_scan,'add-man':cmd_add_man,'add-auto':cmd_add_auto,'list':cmd_list,'remove':cmd_remove,'reset':cmd_reset,'log':cmd_log,'get-last':cmd_link,'redl':cmd_redown,'redl-all':cmd_redown_all,'test-telegram':cmd_test_telegram}
		alias_commands = {'c':cmd_config,'h':cmd_help,'am':cmd_add_man,'aa':cmd_add_auto,'s':cmd_auto_scan,'l':cmd_list,'r':cmd_remove,'rs':cmd_reset,'lg':cmd_log,'gl':cmd_link,'re':cmd_redown,'ra':cmd_redown_all,'t':cmd_test_telegram}
		try:
			if search(r'^[\-]{2}',sys.argv[1]) and sys.argv[1][2:] in commands: commands[sys.argv[1][2:]](sys.argv[2:])
			elif search(r'^[\-]{1}[a-z]+',sys.argv[1]) and sys.argv[1][1:] in alias_commands: alias_commands[sys.argv[1][1:]](sys.argv[2:])
			else: print('USAGE: europlexo [--option]'); cmd_help()
		# script (no command)
		except IndexError:

			# check folders
			if not SERIES_PATH or not os.path.exists(SERIES_PATH): print('WARNING: Series folder not found!\nConfigure your folder path with --config'); exit()
			if not SERIES: print('WARNING: No series found!\nConfigure series with one of the add command.\nFind out more with --help'); exit()
			if not all([check_site(os.path.join(EUROSTREAMING,site)) for _,site,_,_ in SERIES]): exit()
			
			print('## {} ##'.format(EUROSTREAMING))

			# grab info from the series folder
			sf = ScanFolder(SERIES_PATH)

			# run the script for every series
			for name,link,language,mode in SERIES:

				# adjust settings
				print('Searching new episodes for {} [{}]'.format(name,language))
				mode = mode if mode in ['NEW','FULL'] else 'NEW'
				language = language.lower() == 'ENG'.lower()
				link = os.path.join(EUROSTREAMING,link)

				# scan the folder
				sf.scan_serie(name,mode)

				# grab episodes missing
				lf = LinkFinder(link,language)
				eps = sf.episode_missing(lf.info)

				# download every episodes
				for season,episode in eps:
					try:
						_,direct_links = lf.get_direct_links(season,episode)
						print('Downloading {} [{}×{}]'.format(name,season,episode))
						print('Link(s) found:')
						print('\n'.join(['{0:>3}. ({2}) {1}\n'.format(i+1,l,int_to_hr_size(s)) for i,(l,s) in enumerate(direct_links)]))
						download_episode(name,season,episode,direct_links) # downloading
					except ValueError:
						log_line = 'No link found for {} [{}×{}]'.format(name,season,episode)
						if LOG: update_log(log_line), print(log_line)
					print()
			
		# deleting tmp folder
		shutil.rmtree(TMP_PATH)

	# Keyboard Interrupt handler		
	except KeyboardInterrupt: print('\nInterrupt detected. Saving (?) and exit.') 