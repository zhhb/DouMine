import re
import os
import random

from lxml import etree

from mechanize_page_loader import MechanizePageLoader
from selenium_page_loader import SeleniumPageLoader

class BaseScraper:
	page_loader = SeleniumPageLoader()
	# page_loader = MechanizePageLoader()
	
	def __init__(self, id, basedir):
		self.id = id
		self.basedir = basedir
		self.load_existing_data()

	def need_scrape(self):
		return self._results == None
	
	def load_existing_data(self):
		if(not os.access(self.csv_file_path(), os.F_OK)):
			self._results = None
		else:
			csv_file = open(self.csv_file_path())
			csv_content = csv_file.read()
			csv_file.close()
			self._results = csv_content.strip().split("\n")[1:]
	
	def csv_file_path(self):
		return self.basedir + "/" + self._scraper_name() + "." + str(self.id) + ".csv"
	
	def persistent(self):
		if(not os.access(self.basedir, os.F_OK)):
			os.makedirs(self.basedir)
		all_results = self.results()
		
		csv_file = open(self.csv_file_path(), "w")
		csv_file.write("ID\n")
		for result in all_results:
			csv_file.write(result + "\n")
		csv_file.close()
		
	def spawn(self):
		results = map(self._spawn, self.results())
		random.shuffle(results)
		return results
			
	def results(self):
		if(self.need_scrape()):
			self._results = self._actual_fetch_results()
		return self._results
			
	def _actual_fetch_results(self):
		has_more_items = True
		start = 0
		result = []
		
		while(has_more_items):
			page_content = self.load_page(start)
			# Ignore item if 404 error happens
			if(page_content == None):
				break
			
			page_dom = etree.HTML(page_content)
			links = page_dom.xpath(self._data_link())
			data_urls = map(lambda link: link.get("href"), links)
			result_ids = map(lambda url: re.search("http://book.douban.com/\w+/(.+)/", url).group(1), data_urls)
			
			has_more_items = len(result_ids) > 0
						
			for an_id in result_ids:
				result.append(an_id)
			
			start += self._page_size()
				
		return result
		
	def load_page(self, start):
		return BaseScraper.page_loader.load(self._url(start))
		
	# def set_page_loader(self, page_loader):
	# 	self.page_loader = page_loader
