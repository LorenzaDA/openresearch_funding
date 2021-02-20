import pandas as pd
import requests
import os
import json
from bs4 import BeautifulSoup as soup
import numpy as np
from datetime import datetime, timedelta, date
import csv
import re
import nltk
from nltk.tokenize import RegexpTokenizer, word_tokenize
from collections import Counter
from nltk.corpus import stopwords
import time
from random import randint
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
from requests_oauthlib import OAuth2
import re
import numpy as np

from dotenv import load_dotenv
load_dotenv()

def make_soup(url):
    thepage=requests.get(url,headers={'User-Agent': 'Mozilla/5.0'}).text
    soupdata=soup(thepage,"html.parser")
    time.sleep(randint(5,6))
    return soupdata


def nih():
    df=pd.read_excel(os.getenv("directory")+'\\new_grants\\6_28_2020-AllGuideResultsReport.xlsx')

    for i in df['URL']:
        print(i)
        page=make_soup(i)
        with open(os.getenv("directory")+"\\new_grants\\"+i.split("/")[-1:][0], "w",encoding="utf-8") as text_file:
            text_file.write(str(page))
    
def sort_text_nih():
    march=[]
    word=[]
    url=[]
    directory=os.getenv("directory")+"\\nih\\"
    for filename in os.listdir(directory):
        if filename.endswith('.html'):


            words_line=[]
            text_file = open(directory+filename, "r",encoding='utf-8',errors='ignore').read()
            text_file=str(text_file)
            
            #regex =r"(?<=<strong class=\"greybold\">SYNOPSIS</strong>).*(?=<br/>)"
            text_file=soup(text_file,"html.parser").text
            #matches = re.finditer(regex, text_file, re.DOTALL)

            #for matchNum, match in enumerate(matches, start=1):
            #    match=match.group()
            #    match=soup(match,"html.parser").text

            text_tokens = word_tokenize(text_file)
            all_stopwords = stopwords.words('english')
            text_file = [word.lower() for word in text_tokens if not word in all_stopwords and word.isalpha()]

            text_file=" ".join(text_file)

            #data sharing is excluded here
            if any(x in text_file for x in ['open research','open science','open access','replication stud','reproducible research','reproducible result','reproducible code', 'reproducible finding',
                                                        'open code','preregistration','preregistered stud','preprint', 'pre-print', ' registered report', 'open source', 'open software', 'open science framework', 'reproducible method', 'github', 'open data', 'open-access']):
                            for x in ['open research','open science','open access','replication stud','reproducible research','reproducible result','reproducible code', 'reproducible finding',
                                                        'open code','preregistration','preregistered stud','preprint', 'pre-print', ' registered report', 'open source', 'open software', 'open science framework', 'reproducible method', 'github', 'open data', 'open-access']:
                                if x in text_file and x not in words_line:
                                    print(filename,x)

                                    words_line.append(x)
                                    if filename.split("-")[0]=="PA" or filename.split("-")[0]=="PAR" :
                                        url.append('https://grants.nih.gov/grants/guide/pa-files/'+filename)
                                    else:
                                        url.append('https://grants.nih.gov/grants/guide/rfa-files/'+filename)

                                    march.append(text_file)
            if len(words_line) != 0:
                        word.append(words_line)
       
    url=list(dict.fromkeys(url))
    march=list(dict.fromkeys(march))
    print(len(march),len(word),len(url))
    df1 = pd.DataFrame( {'fulltext': march,'word_found': word,'url':url })
    print(df1)

    df1.to_csv(os.getenv("directory")+"\\results\\"+'nih_results.csv', index=False, header=False)

#sort_text_nih()
def ahrc():

    urls=[]
    granturls=[]
    descript=[]
    closingdate=[]
    titles=[]
    page=make_soup("https://ahrc.ukri.org/funding/apply-for-funding/current-opportunities/?pageNum=2&numPerPage=100&sortBy=callCloseDate&sortOrder=DESC")
    pagediv=page.find("div",{"class":"page-news"})
    #print(pagediv)
    for tdatabest in (pagediv.findAll("a")):
        urls.append("http://ahrc.ukri.org"+tdatabest['href'])
    print(urls)
    for i in urls:
        print(i)
        page2=make_soup(i)
        content=str(page2.find("div",{"class":"col-sm-9 content body"}))
        match1=r'<h2 class=\"opportunity-title\">Summary</h2>(.|\n)*?<h2 class=\"opportunity-title\">'
        match2=r'<h2 class=\"opportunity-title\">Closing Dates</h2>(.|\n)*?<h2 class=\"opportunity-title\">'
        matches_summary = soup(re.search(match1, content, re.DOTALL | re.MULTILINE).group(),"html.parser").text
        matches_closingdate = soup(re.search(match2, content, re.DOTALL | re.MULTILINE).group(),"html.parser").text
        title=str(page2.find("h1",{"class":"pull-left"}))
        #print(matches_summary)
        print(matches_closingdate)
        granturls.append(i)
        if len(matches_closingdate)==0:
            closingdate.append(np.nan)
        else:
            closingdate.append(matches_closingdate)
        descript.append(matches_summary)
        titles.append(title)
    df1 = pd.DataFrame( {'fulltext': descript,"title":titles,'url':granturls,'closingdate': closingdate, })
    df1.to_csv(os.getenv("directory")+'\\uk_research\\ahrc.csv', index=False, header=True,encoding = 'utf-8-sig')

#ahrc()

def esrc():
    urls=[]
    granturls=[]
    descript=[]
    title=[]
    url='https://esrc.ukri.org/funding/funding-opportunities/?selectedContentTypes=&selectedCategories=&selectedPublishDates=&selectedStatuses=1%5F1%2C1%5F2&sortby=fundingClosingDate&sortorder=asc&rowsPerPage=100'
    page=make_soup(url)
    pagediv=page.find("section",{"class":"news-list"})
    for i in pagediv.findAll('a'):
        if i['href'][:8]=='/funding':
            urls.append("https://esrc.ukri.org"+i['href'])
    print(urls)
    for i in urls:
        print(i)
        page2=make_soup(i)
        content=str(page2.find("div",{"class":"article-text"}).text)
        content2=str(page2.find("div",{"class":"page-heading"}).text)

        granturls.append(i)
        descript.append(content)
        title.append(content2)
    df1 = pd.DataFrame( {'fulltext': descript,'title': title,'url':granturls})
    df1['closingdate']=""
    df1.to_csv(os.getenv("directory")+'\\uk_research\\esrc.csv', index=False, header=True,encoding = 'utf-8-sig')
#esrc()

def mrc():
    url='https://mrc.ukri.org/funding/browse/?filtersSubmitted=true&callSortBy=callClosingDate&callSortOrder=asc&fcPerPage=100&textSearch=Search+funding...&callStatus=Open'
    urls=[]
    granturls=[]
    descript=[]
    title=[]
    closing=[]
    page=make_soup(url)
    pagediv=page.find("section",{"class":"module text"})
    for i in pagediv.findAll('a'):
        if i['href'][:8]=='/funding':
            urls.append("https://mrc.ukri.org"+i['href'])
    print(urls)
    for i in urls:
        print(i)
        page2=make_soup(i)
        if page2.find("section",{"class":"module text"}) is not None:
            content=str(page2.find("section",{"class":"module text"}).text)
            print("hello")

            closingdate=str(page2.find("li",{"class":"closing"}).text)
            titles=str(page2.find("h1",{"class":"pageTitle"}).text)
            granturls.append(i)
            descript.append(content)
            title.append(titles)
            closing.append(closingdate)

    df1 = pd.DataFrame( {'fulltext': descript,'title': title,'url':granturls,'closingdate':closing })
    df1.to_csv(os.getenv("directory")+'\\uk_research\\mrc.csv', index=False, header=True,encoding = 'utf-8-sig')
#mrc()
def grant_analysis():
    #all_filenames=os.listdir(os.getenv("directory")+'\\uk_research')
    #combined_csv = pd.concat([pd.read_csv(os.getenv("directory")+'\\uk_research\\'+f) for f in all_filenames ])
#export to csv
    #combined_csv.to_csv( os.getenv("directory")+"//results//ukri.csv", index=False, encoding='utf-8-sig')
    combined_csv=pd.read_csv( os.getenv("directory")+"//results//ukri.csv")
    combined_csv['filteredword']=combined_csv['fulltext'].apply(lambda x: sorttext(x))
    combined_csv.to_csv( os.getenv("directory")+"//results//ukri.csv", index=False, encoding='utf-8-sig')

def sorttext(text):
    word=[]
    text=str(text)
    if 'nan' != text.lower():
        all_stopwords = stopwords.words('english')

        text_tokens = word_tokenize(text)
        
        tokens_without_sw = [word.lower() for word in text_tokens if not word in all_stopwords and word.isalpha()]
        
        #tokens_without_sw = [word for word in " ".join(tokens_without_sw) if word.isalpha()]

        tokens_without_sw=" ".join(tokens_without_sw)
        #print(tokens_without_sw)
        for x in ['open research','open science','open access','replication stud','reproducible research','reproducible result','reproducible code', 'reproducible finding',
                                                        'open code','preregistration','preregistered stud','preprint', 'pre-print', ' registered report', 'open source', 'open software', 'open science framework', 'reproducible method', 'github', 'open data', 'open-access','data sharing']:
             if x in tokens_without_sw:
                word.append(x)
    return word

#grant_analysis()        






    
















print("endofscript")  





