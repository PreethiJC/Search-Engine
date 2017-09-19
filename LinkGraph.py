from elasticsearch import Elasticsearch
import time


start_time = time.time()
es = Elasticsearch()

page = es.search(
    index='hw3_crawl',
    doc_type='document',
    scroll='2m',
    size=1000,
    body={
       "stored_fields": ["outlinks"]
    })
sid = page['_scroll_id']
scroll_size = page['hits']['total']

# Start scrolling
linkgraph = {}
while (scroll_size > 0):
    print "Scrolling..."
    page = es.scroll(scroll_id=sid, scroll='2m')
    # Update the scroll ID
    sid = page['_scroll_id']
    # Get the number of results that we returned in the last scroll
    scroll_size = len(page['hits']['hits'])
    print "scroll size: " + str(scroll_size)
    for hit in page['hits']['hits']:
        inlink = hit['_id']
        outlinks = set(hit.get('fields').get('outlinks')[0].split('\n'))
        for ol in outlinks:
            if ol in linkgraph:
                linkgraph[ol].append(inlink)
            else:
                linkgraph[ol] = [inlink]

outputFile = open("/Users/Zion/Desktop/NEU/Sem 2/Information Retrieval/Files1/linkgraph.txt", "w")
for ol in linkgraph:
    line = ol
    for il in linkgraph[ol]:
        line += ' ' + il
    outputFile.write(line.encode('ascii', 'ignore') +'\n')
outputFile.close()

temp = time.time()-start_time
print(temp)
hours = temp//3600
temp = temp - 3600*hours
minutes = temp//60
seconds = temp - 60*minutes
print('%d:%d:%d' %(hours,minutes,seconds))

