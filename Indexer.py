import time
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import os
import re

es = Elasticsearch()
path = "/Users/Zion/Desktop/NEU/Sem 2/Information Retrieval/Files_demo/"
start_time = time.time()
i = 0
for filename in os.listdir(path):
    if (filename != '.DS_Store'):
        file = open(path+filename)
        page = file.read()
        validPage = "<root>" + page + "</root>"
        soup = BeautifulSoup(validPage, 'html.parser')
        i += 1
        texts = soup.find_all('text')
        outlinks = soup.find_all('outlinks')
        text =""
        outlink = ""
        for txt in texts:
            text += txt.get_text().strip()
        for outlnk in outlinks:
            outlink += outlnk.get_text().strip()
        # count = 0
        # for line in text.splitlines():
        #     word = re.sub('\s+', ' ', line).strip().split(' ')
        #     count += len(word)
        jsonDoc = {
            'text': text,
            'outlinks': outlink,
            'author': soup.author.text.strip()
        }
        res = es.index(index="hw3_crawl_demo", doc_type='document', id=soup.docno.text.strip(), body=jsonDoc)
        print("Indexed %d document" % i)

temp = time.time()-start_time
print(temp)
hours = temp//3600
temp = temp - 3600*hours
minutes = temp//60
seconds = temp - 60*minutes
print('%d:%d:%d' %(hours,minutes,seconds))