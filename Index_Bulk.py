from elasticsearch import Elasticsearch
from elasticsearch import helpers
import os
from bs4 import BeautifulSoup
import time

es = Elasticsearch(hosts=['localhost:9200'])
path = "/Users/Zion/Desktop/NEU/Sem 2/Information Retrieval/Files1/"
start_time = time.time()
i = 0
j = 0
actions = []
for filename in os.listdir(path):
    if (filename != '.DS_Store'):
        file = open(path+filename)
        page = file.read()
        validPage = "<root>" + page + "</root>"
        soup = BeautifulSoup(validPage, 'html.parser')

        i += 1
        texts = soup.find('text')
        outlinks = soup.find('outlinks')
        count = 0

        action = {
            "_index": "hw3_crawl",
            "_type": "document",
            "_id": soup.docno.text.strip(),
            "_source": {
                "text": texts.text.strip(),
                "outlinks": outlinks.text.strip(),
            }
        }
        actions.append(action)
        # print("Adding %d document for indexing" % i)
        if (i == 100):
            helpers.bulk(es, actions)
            print("Indexed %d batch" % j)
            i = 0
            j+=1

if i > 0:
    helpers.bulk(es, actions)

temp = time.time()-start_time
print(temp)
hours = temp//3600
temp = temp - 3600*hours
minutes = temp//60
seconds = temp - 60*minutes
print('%d:%d:%d' %(hours,minutes,seconds))

