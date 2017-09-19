# Search-Engine
World War II Search Engine

#### Canonicalizer.py
The purpose of this program is to canonicalize the URLs. Many URLs can refer to the same web resource. In order to ensure that the program crawls 20,000 distinct web sites, the following canonicalization rules should be applied to all URLs encountered.

1. Convert the scheme and host to lower case:  
   ```HTTP://www.Example.com/SomeFile.html → http://www.example.com/SomeFile.html```
2. Remove port 80 from http URLs, and port 443 from HTTPS URLs:  
  ```http://www.example.com:80 → http://www.example.com```
3. Make relative URLs absolute:  
  If you crawl ```http://www.example.com/a/b.html``` and find the URL ```../c.html```, it should canonicalize to ```http://www.example.com/c.html```
4. Remove the fragment, which begins with #:  
  ```http://www.example.com/a.html#anything → http://www.example.com/a.html```
5. Remove duplicate slashes:  
  ```http://www.example.com//a.html → http://www.example.com/a.html```

#### Crawler-1.py
The purpose of this program is to crawl 20000 webpages from the following seed URLs:  
> http://www.history.com/topics/world-war-ii  
> http://en.wikipedia.org/wiki/World_War_II  
> http://en.wikipedia.org/wiki/List_of_World_War_II_battles_involving_the_United_States  
> http://en.wikipedia.org/wiki/Military_history_of_the_United_States_during_World_War_II  

The crawler will manage a frontier of URLs to be crawled. The frontier will initially contain just the seed URLs. URLs will be added to the frontier as the program crawls, by finding the links on the crawled web pages.

Following rules were imposed in the program:
1. The next URL to be crawled from the frontier should be chosen using a best-first strategy. See Frontier Management, below.
2. The crawler must strictly conform to the politeness policy detailed in the section below. 
3. Only HTML documents should be crawled. However, do not reject documents simply because their URLs don’t end in .html or .htm.
4. All outgoing links on the pages being crawled must be found, canonicalized, and added to the frontier if they are new.
5. For each page crawled, the following must be stored and filed with ElasticSearch : an id, the URL, the HTTP headers, the page contents cleaned (with term positions), the raw html, and a list of all in-links (known) and out-links for the page.

##### *Politeness Policy*
The crawler strictly observes this politeness policy at all times.

1. Make no more than one HTTP request per second from any given domain. Crawling multiple pages from different domains at the same time can be done as long as the crawler obeys this rule. The simplest approach is to make one request at a time and have the program sleep between requests.
2. Before the first page is crawled from a given domain, fetch its robots.txt file and make sure that the crawler strictly obeys the file. A third party library is used to parse the file and tell which URLs are OK to crawl.

##### *Frontier Management*
The frontier is the data structure used to store pages needed to be crawled. For each page, the frontier should store the canonicalized page URL and the in-link count to the page from other pages that have been already crawled. When selecting the next page to crawl, the next page is chosen in the following order:

1. Seed URLs should always be crawled first.
2. Must use BFS as the baseline graph traversal (variations and optimizations allowed)
3. Prefer pages with higher in-link counts.
4. If multiple pages have maximal in-link counts, choose the option which has been in the queue the longest.  

If the next page in the frontier is at a domain that the crawler recently crawled a page from, then, instead of waiting, just crawl the next page from a different domain instead.  

##### *Document Processing*
Once a web page is downloaded, it needs to be parsed in order to update the frontier and save its contents. Beautiful Soup 4 is used to do the following:

1. Extract all links in <a> tags. Canonicalize the URL, add it to the frontier if it has not been crawled (or increment the in-link count if the URL is already in the frontier), and record it as an out-link in the link graph file.
2. Extract the document text, stripped of all HTML formatting, JavaScript, CSS, and so on. Write the document text to a file in the same format as the AP89 corpus, as described below.  
   Use the canonical URL as the DOCNO. If the page has a <title> tag, store its contents in a <HEAD> element in the file. 
3. Store the entire HTTP response separately.
