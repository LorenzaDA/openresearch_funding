######################
# 0. Source file for web scraping
######################
# AIM: environment prep and functions for web scraping from NIH & UKRI websites
# DISCLAIMER: other websites should be consulted for funding opportunities mentioning
# open science terms (e.g., the NWO website), but we could not collect their data
# due to permissions


######
# environment prep
#####

# load packages

import pandas as pd
import requests
import os
import json
from bs4 import BeautifulSoup as soup
import numpy as np
from datetime import datetime, timedelta, date
import csv
import nltk
from nltk.tokenize import RegexpTokenizer, word_tokenize
from collections import Counter
from nltk.corpus import stopwords
import time
from random import randint
import re
import numpy as np


# load .env file (environment variable file)

from dotenv import load_dotenv

os.environ["directory"]='/Users/lorenzadallaglio/Documents/riots/scraping_OR_funds/'
load_dotenv()
print(os.getenv("directory"))



######
# Functions
######

# get html text

def make_soup(url):
    thepage=requests.get(url,headers={'User-Agent': 'Mozilla/5.0'}).text
    soupdata=soup(thepage,"html.parser")
    time.sleep(randint(5,6))
    return soupdata


# get list of funding from NIH
# NB change paths to yours - make sure to take into account mac/windows diff.
# mac / , windows \\ for paths

def download_nih():
    print(os.getenv('directory'))
    r=requests.get('https://search.grants.nih.gov/guide/api/excel?perpage=1300&sort=reldate:desc&from=0&type=active,activenosis&parentic=all&primaryic=all&activitycodes=all&doctype=all&parentfoa=all&daterange=01021991-02202021&clinicaltrials=all&fields=all&spons=true&query=')
    df=r.json()
    # save the info to json
    with open(os.getenv("directory")+'/nih/Grants.json', 'w') as json_file:
        json.dump(df, json_file)
        # scrape each URL in the json & save in directory
        # note: this will be ~1000 or more files and takes ~1 hour
    for i in df:
        print(i)
        page=make_soup(i['URL'])
        with open(os.getenv("directory")+"/nih/"+i['URL'].split("/")[-1:][0], "w",encoding="utf-8") as text_file:
            text_file.write(str(page))



# sort text of nih grants

def sort_text_nih():
    march=[]
    word=[]
    url=[]
    descript=[]
    directory=os.getenv("directory")+"/nih/"
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            # for each file from the nih, read the file as a string
            text_file = open(directory+filename, "r",encoding='utf-8',errors='ignore').read()
            text_file=str(text_file)
            text_file=soup(text_file,"html.parser").text
            # apply sort text function
            descript.append(sort_text(text_file))
            # obtain the url of the funding from the html
            if filename.split("-")[0]=="PA" or filename.split("-")[0]=="PAR" :
                 url.append('https://grants.nih.gov/grants/guide/pa-files/'+filename)
            else:
                 url.append('https://grants.nih.gov/grants/guide/rfa-files/'+filename)
    # from the scraping we have "word found" & "url" & we merge it with the initial json file
    # json file has higher level attributes for funding (e.g. start date / end date)
    df1 = pd.DataFrame( {'word_found': descript,'url':url })
    df2 = pd.read_json(directory+"Grants.json")
    df1=df1.merge(df2, left_on='url',right_on='URL', how='left')
    # keep certain info only
    df1.columns=['words','url','title','release_date','Expired_Date','Activity_Code','Parent_Organization','Organization','Participating_Orgs','Document_Number','Document_Type','Clinical_Trials','URL']
    df1=df1[['words','title','release_date','Expired_Date','Clinical_Trials','url']]
    df1.columns=['words','title','release_date','Expired_Date','Clinical_Trials','url']
    #  export
    df1.to_csv(os.getenv("directory")+"/results/"+'nih.csv', index=False, header=True)


# function for scraping in ukri website

def ukri():
    # create empty lists where to put the info
    descript=[]
    urls=[]
    granturls=[]
    funder=[]
    funding_type=[]
    closing_date=[]
    opening_date=[]
    publication_date=[]
    total_fund=[]
    titles=[]
    grant_status=[]
    # scrape through the pages to obtain high level funding data
    # NB adapt number according to how many pages available
    for j in list(range(1, 6)):
        # for each webpage
        if j == 1:
            # for the first page use this link (it is different than the other pages links!)
            # this link is already for open or upcoming opportunities from certain funding counsils only
            page=make_soup("https://www.ukri.org/opportunity/?filter_council%5B0%5D=814&filter_council%5B1%5D=818&filter_council%5B2%5D=824&filter_status%5B0%5D=open&filter_status%5B1%5D=upcoming&filter_order=publication_date&filter_submitted=true")
        else:
            # for the other pages, the url changes
            page=make_soup("https://www.ukri.org/opportunity/page/"+str(j)+"/?filter_council%5B0%5D=814&filter_council%5B1%5D=818&filter_council%5B2%5D=824&filter_status%5B0%5D=open&filter_status%5B1%5D=upcoming&filter_order=publication_date&filter_submitted=true")
        pagediv=page.find("div",{"class":"site-content"})
        # find url on the page & append
        for i in pagediv.findAll("div",{"class":"entry-header"}):
            for aurl in (i.findAll("a")):
                urls.append(aurl['href'])
    # scrape urls to get detailed information
    for i in urls:
        page=make_soup(i)
        page=page.find("main",{"class":"govuk-main-wrapper ukri-main-content"})
        print(page.h1.string)
        #title
        titles.append(page.h1.string)

        #grant summary
        summary_table=page.find("dl",{"class":"govuk-table opportunity__summary"})

        summary_table_headers=[]
        for summary_rows in summary_table.findAll("div",{"class":"govuk-table__row"}):
            summary_table_headers.append(summary_rows.find("dt",{"class":"govuk-table__header opportunity-cells"}).string)
        summary_table_headers=sorted(summary_table_headers)
        #set fields to collect
        collection_set=["Funders: ","Opportunity status: ","Funding type: ","Total fund: ","Publication date: ","Opening date: ","Closing date: "]
        collection_dict={'Funders: ':funder,"Opportunity status: ":grant_status,'Funding type: ':funding_type,"Total fund: ":total_fund,"Publication date: ":publication_date,"Opening date: ":opening_date,"Closing date: ":closing_date}
        data_collection=[funder,grant_status,funding_type,total_fund,publication_date,opening_date,closing_date]
        data_collection1=[]
        # to account for different availability of info across pages
        for l in summary_table_headers:
            if collection_dict.get(l)!=None:
                data_collection1.append(collection_dict.get(l))
        # take info
        header_diff=set(collection_set).difference(summary_table_headers)
        header_inter= list(set(sorted(collection_set)) & set(summary_table_headers))
        for summary_rows in summary_table.findAll("div",{"class":"govuk-table__row"}):
            for j in header_inter:
                if summary_rows.find("dt",{"class":"govuk-table__header opportunity-cells"}).string ==j:
                    collection_dict.get(j).append(summary_rows.find("dd",{"class":"govuk-table__cell opportunity-cells"}).text)
        if header_diff:
            for k in header_diff:
                collection_dict.get(k).append("N/A")


        # Open research text - if any field is missing, append blank
        try:
            description_section=page.find("div",{"class":"govuk-accordion ukri-accordion"}).text
            descript.append(sort_text(description_section))
        except:
            descript.append("")
    # to organise the output into a df from lists
    df1 = pd.DataFrame( {
    'matching_text': descript,
    "granturls":urls,
    "funder":funder,
    "funding_type":funding_type,
    "closing_date":closing_date,
    "opening_date":opening_date,
    "publication_date":publication_date,
    "total_fund":total_fund,
    "titles":titles,
    "status":grant_status})
    print(df1)
    df1.to_csv(os.getenv("directory")+'/results/ukri.csv', index=False, header=True,encoding = 'utf-8-sig')



# to combine the info from the nih and ukri

def combine_funders():
    # read results from scraping
    nih=pd.read_csv(os.getenv("directory")+'/results/'+'nih.csv')
    nih =nih.rename(columns={'words': 'matching_text', 'url': 'granturls','Expired_Date':"closing_date","release_date":"opening_date","title":"titles"})
    ukri=pd.read_csv(os.getenv("directory")+'/results/'+'ukri.csv')
    # join results
    combined_csv = ukri.append(nih)
    # if in the matching text there is data sharing or a blank, or an empty array, remove row
    # NB data sharing was removed bc it is mentioned in ALL nih grants, even when open data is not necessary
    combined_csv=combined_csv[~combined_csv['matching_text'].isin(['[]','',"['data sharing']"])]
    combined_csv = combined_csv[combined_csv['matching_text'].notnull()]
    # sort
    combined_csv=combined_csv.sort_values(['matching_text'], ascending=False)
    #export to csv
    combined_csv.to_csv( os.getenv("directory")+"//results//combined_results.csv", index=False, encoding='utf-8-sig')



# sort the text of the grants

def sort_text(text):
    word=[]
    text=str(text)
    if 'nan' != text.lower():
        # remove stopwords (e.g., and, I, is) - words which provide no meaning - from the html description
        # this is for the search. stopwords might make it harder to find the search terms
        all_stopwords = stopwords.words('english')
        # split the words for the stopwords
        text_tokens = word_tokenize(text)
        # make everything lower case, taking away stopwords
        tokens_without_sw = [word.lower() for word in text_tokens if not word in all_stopwords and word.isalpha()]
        # join the words back again
        tokens_without_sw=" ".join(tokens_without_sw)
        # search the text for selected words for open science
        for x in ['open research','open science','open access','replication stud','reproducible research','reproducible result','reproducible code', 'reproducible finding',
                                                        'open code','preregistration','preregistered stud','preprint', 'pre-print', ' registered report', 'open source', 'open software', 'open science framework', 'reproducible method', 'github', 'open data', 'open-access','data sharing']:
            # if you find one of these words, append to word list and return it
             if x in tokens_without_sw:
                word.append(x)
    return word
