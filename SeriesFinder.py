from bs4 import BeautifulSoup as bs
import requests
from re import search
import os

def find_real_page(url):
	soup = bs(requests.get(url).text,'html.parser')
	real_url = [m for m in [search(r'(?:go\_to\"\:\")([^\s]+)(?:\"\}\;)',str(sc)) for sc in soup.find_all('script')] if m]
	if real_url: real_url = real_url[0].group(1).replace('\\','')
	return real_url if real_url else url

def get_suggestion_list(eurostreaming_url,search):
	soup = bs(requests.get(eurostreaming_url+"/?s="+search.lower().replace(r'\s','+')).text,'html.parser')
	series = {serie.find('a').get('title'):find_real_page(serie.find('a').get('href')) for serie in soup.find_all('h2') if serie.find('a')}
	return series

def print_pretty_formatting(suggestions):
	print('\n'.join(['{:<4}{} [{}]'.format(i+1,series,url) for i,(series,url) in enumerate(suggestions.items())]))