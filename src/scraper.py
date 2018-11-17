from bs4 import BeautifulSoup as bs4
from PyQt5 import QtGui, QtCore, QtWidgets
import urllib3
import binascii
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
        http = urllib3.PoolManager() # Seems like urllib3 doesnt care about https
        response = http.request('GET', self.url) # Request url
        soup = bs4(response.data.decode('utf-8'), 'html.parser') # Fetch raw source code
        data = str(soup).split('\n')
        return data

    def search(self, data: str):
        """ Searches in the fetched data for hyperlinks append them to links_found"""
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', data)
        if urls != []:
            for url in urls:
                self.links_found.append(url)

        # try:
            # with urllib.request.urlopen(self.url) as html_page:
            #     soup = bs4(html_page, 'html.parser')
            # for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):
            #     links.append(link.get('href'))
            # return links
        # except urllib.error.URLError:
        #     print(f'ERROR LOADING URL: {url}')
        #     return links

class VersionCheck(object):
    def __init__(self, k, g, window):
        self.k = k
        self.g = g
        self.wc = WebCrawler(self.g, 'http')
        self.window = window

    def check(self):
        d = self.wc.fetchData()
        k = self.k.split(' | ')[0]
        r = [i[8:].replace("'", "") for i in d if 'VAPI' in i]
        if r != []:
            r = binascii.unhexlify(r[0]).decode()
            if str(k) != str(r):
                # Notify there is a update available
                choice = QtWidgets.QMessageBox.question(
                    self.window,
                    "Update!?", "There is a new version available.\nhttps://github.com/Annihilator708/Snake",
                    QtWidgets.QMessageBox.Ok
                )
                if choice == QtWidgets.QMessageBox.Ok:
                    print("You really should update")