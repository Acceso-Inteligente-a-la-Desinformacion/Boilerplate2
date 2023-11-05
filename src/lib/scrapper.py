from bs4 import BeautifulSoup
from urllib import request, parse

import re

import ssl, os
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl,'_create_unverified_context', None)):
    ssl._create_default_https_context=ssl._create_unverified_context

class Scrapper:
    def __init__(self, url, type:str = "html.parser"):
        self.url = url
        self.type = type
    
    def post(self, data):
        data = parse.urlencode(data).encode()
        req =  request.Request(self.url, data=data)
        html = request.urlopen(req)
        self.soup = BeautifulSoup(html, self.type)
        return self
        
    def get(self):
        html = request.urlopen(self.url)
        self.soup = BeautifulSoup(html, self.type)
        return self

    def select(self, selector:str):
        return self.soup.select(selector)
    
    def selectOne(self, selector:str):
        return self.soup.select_one(selector)
    
    def find(self, element, className):
        return self.soup.find_all(element, {"class": className})
    
    def findOne(self, element, className):
        return self.soup.find(element, {"class": className})
    
    def filterPrice(self, text: str):
        return re.compile('\d+,\d+').search(text).group()
    
    def textIfExists(self, selector, default="Desconocido"):
        if(selector != None):
            return selector.text
        else:
            return default