from threading import Thread
import requests
import time
from bs4 import BeautifulSoup
import urllib.parse
import urllib.robotparser
import queue
import Canonicalizer
from collections import OrderedDict


class LinkStore:

    def __init__(self):
        self.inLinks = set()
        self.outLinks = set()
        self.generation = 99
        self.level = 9999

def getIfValidUrl(link, domain):

    if ':' not in link and 'Main_Page' not in link and 'index' not in link and "?" not in link and "=" not in link and link != "" and link != '/':
        if '#' in link and 'cite' not in link.lower():
            if domain == "http://www.en.wikipedia.org" and '/wiki/' in link.lower():
                return True
            else:
                return False
        elif 'cite' in link.lower() or '#' in link:
            return False
        else:
            return True
    return False

def robotTxt(canonicalURL):
    robotParser = urllib.robotparser.RobotFileParser()
    if robotParser.set_url(canon.get_domain(canonicalURL) + "/robots.txt") != None:
        robotParser.read()
        crawlDelay = robotParser.crawl_delay("*")
        if crawlDelay == None:
            crawlDelay = 1
        checkURL = robotParser.can_fetch(canonicalURL, "*")
    else:
        crawlDelay = 1
        checkURL = True
    return checkURL, crawlDelay

def open_url(url):

    blackListURLs = ["http://en.wikipedia.org/wiki/International_Standard_Book_Number", "http://en.wikipedia.org/wiki/JSTOR",
                     "http://en.wikipedia.org/wiki/Digital_object_identifier", "http://en.wikipedia.org/wiki/Cambridge_University_Press",
                     "http://en.wikipedia.org/wiki/Routledge", "http://en.wikipedia.org/wiki/Osprey_Publishing", "http://en.wikipedia.org/wiki/OCLC"]
    blackListURLs = set(blackListURLs)
    keywords = ["world", "war", "ww2", "wwii", "united", "states", "u.s", "u.s.a", "america", "battles", "won",
                "military", "nazi", "japan", "germany", "pearl", "harbor"]
    # keywords = ["world", "war", "ww2", "wwii", "battles", "won", "operation", "torch", "colmar", "ruhr", "doolittle"
    #             "military", "nazi", "japan", "germany", "pearl", "harbor"]
    keywords = set(keywords)
    global frontier, visited_urls, level, levelDict, discoveredTillNow

    if len(frontier) >= 20000:
        return
    i = 0
    canonicalURL = canon.canonicalize(url)
    checkURL, crawlDelay = robotTxt(canonicalURL)
    if(checkURL):
        print("Crawling:", canonicalURL)
        visited_urls.add(canonicalURL)
        try:
            data = requests.get(canonicalURL)
        except:
            print("Could not access", canonicalURL)
            return

        if "text/html" not in data.headers["content-type"]:
            return
        soup = BeautifulSoup(data.text, 'html.parser')
        links = soup.find_all('a', href = True)

        for link in links:
            if len(set(link.text.lower().split(' ')) & keywords) >= 1:
                if getIfValidUrl(link.get('href'), canon.get_domain(canonicalURL)):
                    urlJoined = canon.canonicalize(urllib.parse.urljoin(canonicalURL, link['href']))
                    if urlJoined not in blackListURLs:
                        frontier[url].outLinks.add(urlJoined)
                    if (urlJoined[0:4] == 'http' and urlJoined not in visited_urls and urlJoined not in blackListURLs):
                        new = True
                        for lev in levelDict:
                            if urlJoined in levelDict[lev]:
                                new = False
                                break

                        if (discoveredTillNow < 20000 and new):
                            if frontier[url].level-1 not in levelDict:
                                levelDict[frontier[url].level-1] = OrderedDict()
                            levelDict[frontier[url].level - 1][urlJoined] = LinkStore()
                            levelDict[frontier[url].level - 1][urlJoined].generation = generation - 1
                            levelDict[frontier[url].level - 1][urlJoined].level = frontier[url].level - 1
                            discoveredTillNow += 1
                        else:
                            break

                    if (urlJoined not in blackListURLs):
                        if urlJoined in frontier:
                            frontier[urlJoined].inLinks.add(canonicalURL)
                        else:
                            exist = False
                            l = -1
                            for lev in levelDict:
                                if urlJoined in levelDict[lev]:
                                    exist = True
                                    l = lev
                                    break
                            if exist:
                                levelDict[l][urlJoined].inLinks.add(canonicalURL)


        print("Pausing for politeness: " + str(crawlDelay))
        time.sleep(crawlDelay)
    else:
        print("Forbidden URL: ", canonicalURL)
        return

def crawl():
    global frontier, visited_urls, level, levelDict, discoveredTillNow
    threads = []

    t_start = time.time()
    # print(len(frontier))
    if len(frontier) < 50:
        threadCount = len(frontier)
    else:
        threadCount = 50

    i = 0
    for f in frontier:
        if i == threadCount:
            break
        if f not in visited_urls:
            t = Thread(target=open_url, args=(f,))
            t.start()
            threads.append(t)
            i += 1

    for t in threads:
        t.join()

    if i == 0:
        levelDict[level] = frontier
        frontier = OrderedDict()

    t_end = time.time()
    # print(t_end - t_start)


def wikiCleanUp(soup):
    text = ""
    text_data = []
    for lImages in soup.find_all("div", {"class": "thumb tleft"}):
        lImages.decompose()
    for rImages in soup.find_all("div", {"class": "thumb tright"}):
        rImages.decompose()
    for sup in soup.find_all('sup', {'class': 'reference'}):
        sup.decompose()
    for tables in soup.find_all("table", {"class": "vertical-navbox nowraplinks"}):
        tables.decompose()
    for para in soup.find_all("p"):
        text += para.text + " "
    for table in soup.findAll('table', {'class': 'wikitable'}):
        headers = table.findAll('th')
        rows = table.findAll('tr')
        for tr in rows:
            cols = tr.findAll('td')
            i = 0
            for td in cols:
                tableText = ''.join(td.text)
                if (i < len(headers)):
                    utftext = headers[i].text + ": " + str(tableText.encode('utf-8'))
                else:
                    utftext = str(tableText.encode('utf-8'))
                text_data.append(utftext)  # EDIT
                i += 1
    return text + "\n".join(text_data)

def historyCleanUp(soup):
    text = ""
    if soup.find('article') != None:
        for article in soup.findAll('article'):
            for div in soup.find_all("div", {"class": "extra-tools"}):
                div.decompose()
            for p in article.findAll('p'):
                if p.text not in text:
                    text += p.text.strip() + ' '
    else:
        for div in soup.findAll('div', {'class': 'article'}):
            for p in div.findAll('p'):
                if p.text not in text:
                    text += p.text.strip() + ' '
    return text

level = 9999
levelDict = OrderedDict()
canon = Canonicalizer.Canonicalizer
frontier = OrderedDict()
seed_urls = ["http://www.history.com/topics/world-war-ii", "http://en.wikipedia.org/wiki/World_War_II", "http://en.wikipedia.org/wiki/List_of_World_War_II_battles_involving_the_United_States", "http://en.wikipedia.org/wiki/Military_history_of_the_United_States_during_World_War_II"]
discoveredTillNow = len(seed_urls)

for url in seed_urls:
    frontier[url] = LinkStore()

visited_urls = set()
generation = 99
blackListURLs = ["http://en.wikipedia.org/wiki/International_Standard_Book_Number", "http://en.wikipedia.org/wiki/JSTOR",
                     "http://en.wikipedia.org/wiki/Digital_object_identifier", "http://en.wikipedia.org/wiki/Cambridge_University_Press",
                     "http://en.wikipedia.org/wiki/Routledge", "http://en.wikipedia.org/wiki/Osprey_Publishing", "http://en.wikipedia.org/wiki/OCLC"]
blackListURLs = set(blackListURLs)
keywords = ["world", "war", "ww2", "wwii", "united", "states", "u.s", "u.s.a", "america", "battles", "won", "military", "nazi", "japan", "germany", "pearl", "harbor"]
keywords = set(keywords)
start_time = time.time()
while discoveredTillNow < 20000:
    crawl()
    print(discoveredTillNow)
    generation -= 1
    if len(frontier) == 0:
        level -= 1
        frontier = levelDict[level]
    frontier = OrderedDict(
        sorted(frontier.items(), key=lambda x: (x[1].level, len(x[1].inLinks), x[1].generation), reverse=True))
i = 0
temp = time.time() - start_time
hours = temp // 3600
temp = temp - 3600 * hours
minutes = temp // 60
seconds = temp - 60 * minutes
print('%d:%d:%d' % (hours, minutes, seconds))
start_time = time.time()
for l in levelDict:
    for f in levelDict[l]:
        checkURL, crawlDelay = robotTxt(f)
        cleanText = ""
        try:
            data = requests.get(f)
        except:
            print("Could not access", f)
            continue
        soup = BeautifulSoup(data.text, 'html.parser')
        domain = canon.get_domain(f)
        if domain == "http://en.wikipedia.org":
            cleanText = wikiCleanUp(soup)
        elif domain == "http://www.history.com":
            cleanText = historyCleanUp(soup)
        else:
            for para in soup.find_all("p"):
                cleanText += para.text + " "
        if not levelDict[l][f].outLinks:
            canonicalURL = canon.canonicalize(f)
            links = soup.find_all('a', href=True)
            for link in links:
                if len(set(link.text.lower().split(' ')) & keywords) >= 1:
                    if getIfValidUrl(link.get('href'), canon.get_domain(canonicalURL)):
                        urlJoined = canon.canonicalize(urllib.parse.urljoin(canonicalURL, link['href']))
                        if urlJoined not in blackListURLs:
                            levelDict[l][f].outLinks.add(urlJoined)
        textDesign = "<DOCNO>"+f+"</DOCNO>\n<TEXT>"+cleanText+"</TEXT>\n<INLINKS>"+"\n".join(levelDict[l][f].inLinks)+"</INLINKS>\n<OUTLINKS>"+"\n".join(levelDict[l][f].outLinks)+"</OUTLINKS><AUTHOR>Preethi Chavely</AUTHOR>"
        i+=1
        outputFile = open("/Users/Zion/Desktop/NEU/Sem 2/Information Retrieval/Files/%s" % i, "w+")
        outputFile.write(textDesign)
        outputFile.close()
        time.sleep(crawlDelay)
temp = time.time() - start_time
hours = temp // 3600
temp = temp - 3600 * hours
minutes = temp // 60
seconds = temp - 60 * minutes
print('%d:%d:%d' % (hours, minutes, seconds))
# print(frontier)