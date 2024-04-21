import re 
from pymongo import MongoClient
from urllib.request import urlopen
from urllib.error import URLError
from urllib.error import HTTPError
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from collections import deque 
import ssl

#MongoDB setup
def connectDataBase():

    # Create a database connection object using pymongo
    client = MongoClient('mongodb://localhost:27017/')
    db = client['web_crawler_db']
    return db['pages']


#crawler
def crawlerThread(frontier: deque, collection):
    
    ssl._create_default_https_context = ssl._create_unverified_context

    visitedUrls = set() #stores urls to the database
    #while not frontier.done() do
    while len(frontier) > 0:
        #url <— frontier.nextURL()
        url = frontier.popleft()
        #add to visited
        visitedUrls.add(url)
        #html <— retrieveURL(url)
        try:
            html = urlopen(url)
        except HTTPError as e:
            print(e)
            visitedUrls.add(url)
            continue
        except URLError as e:
            print(e)
            visitedUrls.add(url)
            continue
            
        html = BeautifulSoup(html, 'html.parser')

        page = collection.find_one({'_id': url})
        
        if(page):
            collection.update_one({'_id': url}, {"$set": {'text': str(html) }})
        else:
            collection.insert_one({'_id': url, 'text': str(html)})

       
        #finds Permanent Faculty heading
        if (html.find('h1', string=re.compile('(Permanent Faculty)+'))):
            print(f"Found 'Permanent Faculty' on page: {url}")
            #clear_frontier()
            frontier.clear()
        else:
            anc = html.find_all('a')
            urls = []
            for anc in anc:
                href = anc.get('href')
                urls.append(urljoin(url, href))

            for url in urls:
                if url not in visitedUrls:
                    frontier.append(url)
                    #visit url
                    visitedUrls.add(url)

#connect database
db = connectDataBase()

pages = db.pages

crawlerThread(deque(["https://www.cpp.edu/sci/computer-science/"]), pages)
