from bs4 import BeautifulSoup as bs
import requests
from re import search
from time import sleep

def encrypt2turbovid(linkup_url):
	return requests.get(linkup_url.replace("/tv/","/tva/"),allow_redirects=True).url

def turbovid2turbovidPOST(turbovid_url):
	soup = bs(requests.get(turbovid_url,allow_redirects=True).text, 'html.parser')
	post = {i.get('name'):i.get('value') for i in soup.find_all('input')}
	sleep(6)
	return requests.post(turbovid_url,data=post).text

def turbovidPOST2turbovidCloud(turbovid_post_url):
	try: url = search(r'(?:sources\:\s\[\")([^\s]+)(?:\"\]\,)',turbovid_post_url).group(1)
	except AttributeError: url = None
	return url

def get_TurboVid_download_link(url): return turbovidPOST2turbovidCloud(turbovid2turbovidPOST(encrypt2turbovid(url)))