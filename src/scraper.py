from bs4 import BeautifulSoup as bs4
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from urllib.request import urlopen, Request

import urllib
import random
import ssl, socket
import re


class WebCrawler(object):
    def __init__(self, queue):
        self.queue = queue

    def run(self, url):
        self.fetchData(url=url)

    def search(self, data: str):
        """ Searches in the fetched data for hyperlinks append them to links_found"""
        links_found = []
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', str(data))
        if urls != []:
            for url in urls:
                links_found.append(url)
            self.queue.put(links_found)
            return
        else:
            self.queue.put(links_found)
            return
        
    def fetchData(self, url):
        """Fetches raw data and puts it in a list"""
        desktop_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
                 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']

        if url.startswith('https://') or url.startswith('http://'):
            try:
                resp = urlopen(Request(url, headers={'User-agent' : random.choice(desktop_agents)}), timeout=1)
                response = resp.read()
            except (
                urllib.error.HTTPError,
                urllib.error.URLError,
                ssl.SSLWantReadError,  # raised by a non-blocking SSL socket when trying to read or write data, but more data needs to be received on the underlying TCP transport before the request can be fulfilled.
                socket.timeout, # this exception is raised when a timeout occurs on a socket which has had timeouts enabled via a prior call to settimeout()
                ):
                response = 'No results\n'.encode('utf8')
            
            try:
                soup = bs4(response.decode().strip(), 'html.parser')  # Fetch raw source code
            except UnicodeDecodeError:
                self.queue.put(['Could not decode: {}'.format(url)])
                return
            data = str(soup).split('\n')
            self.search(data)
            return
        else:
            self.queue.put([])
            return

