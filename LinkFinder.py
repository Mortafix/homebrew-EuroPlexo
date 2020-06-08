from bs4 import BeautifulSoup as bs
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from re import findall,search
from dispatcher.DeltaBit import get_DeltaBit_download_link
from dispatcher.TurboVid import get_TurboVid_download_link

class LinkFinder:
	def __init__(self,url,sub=True):
		'''Instance with url,sub and info,soup to compute one-time'''
		self._url = url
		self._sub = sub
		self._soup = bs(requests.get(url).text, 'html.parser')
		self.info = {n:len([e for e in str(div).split('<br/>') if search(r'[0-9]{1,2}×(?!00)[0-9]{1,2}',e)]) for n,div in self._get_seasons_html_div().items()}
	
	def __str__(self):
		'''Pretty printing'''
		info_str = '\n'.join(['Stagione {}: {} episodi(o).'.format(s,e) for s,e in self.info.items()])
		lang_str = 'ENG (SUB ITA)' if self._sub else 'ITA'
		return 'Link: {}\nLanguage: {}\n-- Info --\n{}'.format(self._url,lang_str,info_str)

	def _is_season(self,div):
		'''Check if a html div is a season'''
		try: return div['class'][0] == 'su-spoiler' and ('SUB' in div.text.split('\n')[0]) == self._sub
		except KeyError: return False

	def _is_episode_out(self,season,episode):
		'''Check if an episode is out'''
		return season <= max(self.info) and episode <= self.info[season] 

	def _get_real_season_number(self,div):
		'''Get the real season number (possible seasons missing)'''
		return int(findall(r'(?:[A-Z]+\sSTAGIONE\s)([0-9]{1,2})(?:\s(?:\(SUB\s)?ITA\)?)',str(div))[0])

	def _get_seasons_html_div(self):
		'''Get all seasons in html div'''
		return {self._get_real_season_number(div):div for div in self._soup.find_all('div') if self._is_season(div)}

	def _get_crypted_links(self,season=None,episode=None):
		'''Get html crypted links for an episode, if not specified get last'''
		if not season and not episode: season,episode = list(self.info.items())[-1]
		div = [d for d in str(self._get_seasons_html_div()[season]).split('<br/>') if search(r'[0-9]{1,2}×0?'+str(episode),d)][0]
		return season,episode,findall(r'(?:<a href=\")([^\s]+)(?:\".+?>)([a-zA-Z0-9]+)',div)

	def _site_dispacher(self,link,site):
		'''Call the link finder for every site'''
		sites = {'DeltaBit': get_DeltaBit_download_link,'Turbovid': get_TurboVid_download_link}
		return sites[site](link) if site in sites else None

	def _get_file_size(self,url):
		'''Get file size for video quality'''
		requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
		try: return int(requests.head(url,allow_redirects=True,verify=False).headers.get('Content-Length')) / float(1 << 20)
		except TypeError: return 0

	def get_direct_links(self,season=None,episode=None):
		'''Get all the direct links for an episode, if not specified get last'''
		if season and episode and not self._is_episode_out(season,episode): raise ValueError('Episode {}×{} isn\'t out yet'.format(season,episode))
		else: season,episode,crypted_links = self._get_crypted_links(season,episode)
		direct_links = sorted([(l,self._get_file_size(l)) for l in [self._site_dispacher(l,n) for l,n in crypted_links] if l],key=lambda x:x[1],reverse=True)
		if direct_links: return (season,episode),direct_links
		else: raise ValueError('No link found for episode {}×{}.'.format(season,episode))

if __name__ == '__main__':
	lk = LinkFinder("https://eurostreaming.pet/arrow-episodi-2/")
	print(lk)
	links = lk.get_direct_links()
	print(links)