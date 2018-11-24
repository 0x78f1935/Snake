from bs4 import BeautifulSoup as bs4
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import random
import asyncio
import aiohttp
import re


class WebCrawler(object):
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def search(self, data: str):
        """ Searches in the fetched data for hyperlinks append them to links_found"""
        links_found = []
        urls = re.findall(r'href=[\'"]?([^\'" >]+)', str(data))
        if urls != []:
            for url in urls:
                links_found.append(url)
            return links_found
        else:
            return []
        
    async def fetchData(self, url):
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
            timeout = aiohttp.ClientTimeout(total=1)
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
                print(url)
                try:
                    async with session.get(url, timeout=timeout, headers={'User-agent' : random.choice(desktop_agents)}) as response:
                        response = await response.read()
                        try:
                            soup = bs4(response.decode().strip(), 'html.parser')  # Fetch raw source code
                        except UnicodeDecodeError:
                            return ['Could not decode: {}'.format(url)]
                        data = str(soup).split('\n')
                        return await self.search(data)
                except aiohttp.client_exceptions.ClientConnectorError:
                    return []
                except asyncio.TimeoutError:
                    return []
        else:
            return []
