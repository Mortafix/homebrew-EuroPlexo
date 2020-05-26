from bs4 import BeautifulSoup as bs
import requests
from re import sub,findall
from time import sleep

def encrypt2deltabit(linkup_url):
	return requests.get(linkup_url.replace("delta","adelta"),allow_redirects=True).url

def deltabit2deltabitGen(deltabit_url):
	soup = bs(requests.get(deltabit_url,allow_redirects=True).text, 'html.parser')
	get_attrs = sub(r'download_video|\'|\(|\)','',[l['onclick'] for l in soup.find_all('a') if "onclick" in l.attrs][0]).split(',')
	return 'https://deltabit.co/dl?op=download_orig&id={}&mode={}&hash={}'.format(get_attrs[0],'o',get_attrs[2])

def deltabitGen2deltabitCloud(deltabit_gen_url):
	urls = list()
	while len(urls) == 0:
		urls = findall(r'(?:onclick=\"window.open\(\')([^\s]+)(?:\')',requests.get(deltabit_gen_url).text)
		sleep(1)
	return urls[0]

def get_DeltaBit_download_link(url): return deltabitGen2deltabitCloud(deltabit2deltabitGen(encrypt2deltabit(url)))

if __name__ == '__main__':
	url = "https://linkup.pro/delta/erf3921nri5r"
	down_url = get_DeltaBit_download_link(url) 
	print(down_url)