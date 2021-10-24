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

from dotenv import load_dotenv
load_dotenv()




def make_soup(url):
    thepage=requests.get(url,headers={'User-Agent': 'Mozilla/5.0'}).text
    soupdata=soup(thepage,"html.parser")
    time.sleep(randint(5,6))
    return soupdata


def download_nih():
    r=requests.get('https://search.grants.nih.gov/guide/api/excel?perpage=1300&sort=reldate:desc&from=0&type=active,activenosis&parentic=all&primaryic=all&activitycodes=all&doctype=all&parentfoa=all&daterange=01021991-02202021&clinicaltrials=all&fields=all&spons=true&query=')
    df=r.json()
    with open(os.getenv("directory")+'\\nih\\Grants.json', 'w') as json_file:
        json.dump(df, json_file)

    #df=pd.read_excel(os.getenv("directory")+'\\new_grants\\6_28_2020-AllGuideResultsReport.xlsx')

    for i in df:
        print(i)
        page=make_soup(i['URL'])
        with open(os.getenv("directory")+"\\nih\\"+i['URL'].split("/")[-1:][0], "w",encoding="utf-8") as text_file:
            text_file.write(str(page))
    
def sort_text_nih():
    march=[]
    word=[]
    url=[]
    descript=[]
    directory=os.getenv("directory")+"\\nih\\"
    for filename in os.listdir(directory):
        if filename.endswith('.html'):

            text_file = open(directory+filename, "r",encoding='utf-8',errors='ignore').read()
            text_file=str(text_file)
            
            text_file=soup(text_file,"html.parser").text
            descript.append(sort_text(text_file))
            if filename.split("-")[0]=="PA" or filename.split("-")[0]=="PAR" :
                 url.append('https://grants.nih.gov/grants/guide/pa-files/'+filename)
            else:
                 url.append('https://grants.nih.gov/grants/guide/rfa-files/'+filename)


    #print(len(march),len(word),len(url))
    
    df1 = pd.DataFrame( {'word_found': descript,'url':url })
    df2 = pd.read_json(directory+"Grants.json")
    df1=df1.merge(df2, left_on='url',right_on='URL', how='left')
    df1.columns=['words','url','title','release_date','Expired_Date','Activity_Code','Parent_Organization','Organization','Participating_Orgs','Document_Number','Document_Type','Clinical_Trials','URL']
    df1=df1[['words','title','release_date','Expired_Date','Clinical_Trials','url']]
    df1.columns=['words','title','release_date','Expired_Date','Clinical_Trials','url']
    print(df1)
    df1.to_csv(os.getenv("directory")+"\\results\\"+'nih.csv', index=False, header=True)

def ukri():
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
    for j in list(range(1, 6)):
        if j == 1:
            page=make_soup("https://www.ukri.org/opportunity/?filter_council%5B0%5D=814&filter_council%5B1%5D=818&filter_council%5B2%5D=824&filter_status%5B0%5D=open&filter_status%5B1%5D=upcoming&filter_order=publication_date&filter_submitted=true")
        else:
            page=make_soup("https://www.ukri.org/opportunity/page/"+str(j)+"/?filter_council%5B0%5D=814&filter_council%5B1%5D=818&filter_council%5B2%5D=824&filter_status%5B0%5D=open&filter_status%5B1%5D=upcoming&filter_order=publication_date&filter_submitted=true")
        pagediv=page.find("div",{"class":"site-content"})
        for i in pagediv.findAll("div",{"class":"entry-header"}):
            for aurl in (i.findAll("a")):
                urls.append(aurl['href'])
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
        for l in summary_table_headers:
            if collection_dict.get(l)!=None:
                data_collection1.append(collection_dict.get(l))
        
        header_diff=set(collection_set).difference(summary_table_headers)
        header_inter= list(set(sorted(collection_set)) & set(summary_table_headers))
        for summary_rows in summary_table.findAll("div",{"class":"govuk-table__row"}):
            for j in header_inter:
                if summary_rows.find("dt",{"class":"govuk-table__header opportunity-cells"}).string ==j:
                    collection_dict.get(j).append(summary_rows.find("dd",{"class":"govuk-table__cell opportunity-cells"}).text) 
        if header_diff:
            for k in header_diff:
                collection_dict.get(k).append("N/A")
        
        
        #Open research text
        try:
            description_section=page.find("div",{"class":"govuk-accordion ukri-accordion"}).text
            descript.append(sort_text(description_section))
        except:
            descript.append("")

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
    df1.to_csv(os.getenv("directory")+'\\results\\ukri.csv', index=False, header=True,encoding = 'utf-8-sig')        

def combine_funders():

    nih=pd.read_csv(os.getenv("directory")+'\\results\\'+'nih.csv')
    nih =nih.rename(columns={'words': 'matching_text', 'url': 'granturls','Expired_Date':"closing_date","release_date":"opening_date","title":"titles"})
    ukri=pd.read_csv(os.getenv("directory")+'\\results\\'+'ukri.csv')
    combined_csv = ukri.append(nih)
    combined_csv=combined_csv[~combined_csv['matching_text'].isin(['[]',''])]
    combined_csv = combined_csv[combined_csv['matching_text'].notnull()]
    print(combined_csv.head())
    combined_csv=combined_csv.sort_values(['matching_text'], ascending=False)
    #print(combined_csv)
#export to csv
    combined_csv.to_csv( os.getenv("directory")+"//results//combined_results.csv", index=False, encoding='utf-8-sig')

def sort_text(text):
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






    















