from bs4 import BeautifulSoup as bs4
from PyQt5 import QtGui, QtCore, QtWidgets
import urllib3
import re


class WebCrawler(object):
    def __init__(self, url, protocol):
        self.url = url
        print(self.url)
        self.protocol = protocol
        self.data = self.fetchData()
        self.links_found = []
        
    def fetchData(self):
        """Fetches raw data and puts it in a list"""
        http = urllib3.PoolManager()  # Seems like urllib3 doesnt care about https
        try:
            response = http.request('GET', self.url)  # Request url
        except urllib3.exceptions.MaxRetryError:
            return []
        except urllib3.exceptions.LocationValueError:
            return []
        try:
            soup = bs4(response.data.decode('utf-8').strip(), 'html.parser')  # Fetch raw source code
        except UnicodeDecodeError:
            return ['Could not decode: {}'.format(self.url)]
        data = str(soup).split('\n')
        return data

    def search(self, data: str):
        """ Searches in the fetched data for hyperlinks append them to links_found"""
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', str(data))
        if urls != []:
            for url in urls:
                self.links_found.append(url)