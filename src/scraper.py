from bs4 import BeautifulSoup as bs4
from PyQt5 import QtGui, QtCore, QtWidgets
import urllib3
import binascii
import re
from multiprocessing.pool import ThreadPool
import threading

def threaded(f, daemon=False):
    import Queue

    def wrapped_f(q, *args, **kwargs):
        '''this function calls the decorated function and puts the 
        result in a queue'''
        ret = f(*args, **kwargs)
        q.put(ret)

    def wrap(*args, **kwargs):
        '''this is the function returned from the decorator. It fires off
        wrapped_f in a new thread and returns the thread object with
        the result queue attached'''

        q = Queue.Queue()

        t = threading.Thread(target=wrapped_f, args=(q,)+args, kwargs=kwargs)
        t.daemon = daemon
        t.start()
        t.result_queue = q        
        return t

    return wrap

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
            return [f'No search result found on: {self.url}']
        try:
            soup = bs4(response.data.decode('utf-8').strip(), 'html.parser')  # Fetch raw source code
        except UnicodeDecodeError:
            return [f'Could not decode: {self.url}']
        data = str(soup).split('\n')
        return data

    def search(self, data: str):
        """ Searches in the fetched data for hyperlinks append them to links_found"""
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', data)
        if urls != []:
            for url in urls:
                self.links_found.append(url)

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
            r = r.split(' | ')[0]
            if str(k) != str(r):
                # Notify there is a update available
                choice = QtWidgets.QMessageBox.question(
                    self.window,
                    "Update!?", "There is a new version available.\nhttps://github.com/Annihilator708/Snake",
                    QtWidgets.QMessageBox.Ok
                )
                if choice == QtWidgets.QMessageBox.Ok:
                    print("You really should update")