from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

#MongoDB setup
def connectDataBase():

    # Create a database connection object using pymongo
    client = MongoClient('mongodb://localhost:27017/')
    db = client['web_crawler_db']
    return db['pages']


#connect to db
db = connectDataBase()
#professors collection
professors = db.professors
#pages collections
pages = db.pages

def parser():
    page = pages.find_one({"_id": "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"})
    html = page.get('text')

    bs = BeautifulSoup(html, 'html.parser')
    
    proSection = bs.find('section', {'class':{'text-images'}})

    proHeaders = proSection.find_all('h2')
    proC = list(map(lambda h2: h2.parent, proHeaders))

    for prof in proC:
        #get name
        name = prof.h2.get_text().strip()

        #get title
        title = prof.find("strong", string=re.compile('(Title){1,1}')).next_sibling.get_text()
        
        if (title[0] == ":"):
           title = title[1:]
        #trim
        title = title.strip()

        #get office
        office = prof.find("strong", string=re.compile('(Office){1,1}')).next_sibling.get_text()

        if (office[0] == ":"):
           office = office[1:]
        #trim
        office = office.strip()

        #get phone
        phone = prof.find("strong", string=re.compile('(Phone){1,1}')).next_sibling.get_text()
        if (phone[0] == ":"):
           phone = phone[1:]
        #trim
        phone = phone.strip()
        
        #get email
        email = prof.find('a', {'href': re.compile("^(mailto:)")}).get('href')
        email=email.split(":")[1]

        #get website
        website= prof.find('a', {'href':re.compile('^https{0,1}:\/\/www\.cpp\.edu\/faculty')}).get('href')

        #create document
        Doc = {
            "name":name,
            "title":title,
            "office":office,
            "phone": phone,
            "email":email,
            "website":website
        }

        #insert/update to Mongodb

        curPro = professors.find_one({"_id":name})
        if (curPro):
            professors.update_one({"_id":name}, {"$set":Doc})
        else:
            professors.insert_one(Doc)

parser()