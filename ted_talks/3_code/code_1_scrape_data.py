#!/usr/bin/env python
# coding: utf-8

# TED Talks

""" from json.tool import main """
from pickle import FALSE, TRUE
from tkinter import END
from xml.dom.pulldom import END_DOCUMENT
from numpy import append, concatenate
import pandas as pd
import re
import datetime
import os
import numpy as np
from pandasql import sqldf


#global variables
pysqldf = lambda q: sqldf(q, globals())
dic_scrape={}
list_error=[]
testing=TRUE #Turn to True if testing

def print_var(list_lines):
    s = '''\
    ---------------------------------------------------------------\n
    '''
    for element in list_lines:
        print(s)
        print(element)

def first_data_set(filename):

    raw_data=pd.read_csv(filename)
    df=raw_data.copy()
    #Reporting basic information of df
    # s = '''\
    #     ---------------------------------------------------------------\n
    #     ---------------------------------------------------------------\n
    #     Basic dataframe information\n
    #     Num Rows: {rows}\n
    #     Num Column: {columns}\n
    #     Column Names: {names}
    #     ---------------------------------------------------------------\n
    #     ---------------------------------------------------------------\n
    #    '''.format(rows=df.shape[0], columns=df.shape[1],names=df.columns.values) 
    # print(s)

    return df

def find_url(string):
    # find all urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)      
    return [x[0] for x in url]


def update_dic( var_name, key_value):
    """
    Updates Dictionary
    """
    dic_scrape.update({var_name:key_value})
    return dic_scrape

def build_dic(meta, website):
    """
    This function deconstructs the tag and builds the dictionary
    """
    global dic_scrape, list_error

    #positions in html tag where the targeted data is stored within the meta tag
    positions=[1,27,28,29,30,33,34,35,37]
    for i in positions:
        try:
            if i==1:
                var=(str(meta[i]).split(' '))[1]
                url=find_url(var)[0]
                dic_scrape.update({'url':url})

            elif i==27:
                title=(str(meta[i])).split("=")[1]
                title=title.split('"')[1]
                dic_scrape.update({'title_1':title})
            elif i==28:
                title_2=(str(meta[i])).split("=")[1]
                title_2=title_2.split('"')[1]
                dic_scrape.update({'title_2':title_2})
            elif i==29:
                description_1=(str(meta[i])).split("=")[1][:-5]
                dic_scrape.update({'description_1':description_1})
            elif i==30:
                description_2=(str(meta[i])).split("=")[1][:-5]
                dic_scrape.update({'description_2':description_2})
            elif i==33:
                duration_seg=(str(meta[i])).split(' ')[1]
                duration_seg=int(duration_seg.split('=')[1][1:-1])
                dic_scrape.update({'duration_seg':duration_seg})
            elif i==34:
                a=[]
                keywords=(str(meta[i])).split("=")[1][:-5]
                keywords=keywords[1:-1].split(',')
                dic_scrape.update({'keywords':keywords})
            elif i==35:
                epochtime=int(((str(meta[i])).split("=")[1][:-9])[1:-1])
                release_date = datetime.datetime.fromtimestamp(epochtime)
                dic_scrape.update({'release_date':release_date})
            else: 
                author=(str(meta[i])).split("=")[1]
                author=author.split('"')[1]
                dic_scrape.update({'author':author})
        except:
            info=str(("In", website, " a parsing error occurred during parsing in module 'build_dic', position ", i))
            list_error.append(info)
    return dic_scrape



def soup_data_set(target_website):
    global dic_scrape, list_error
    import urllib
    from bs4 import BeautifulSoup
    import datetime
    
    try:
        html = urllib.urlopen (target_website)
    except:
        info=str(("In", target_website, " The server could not be found."))
        list_error.append(info)

    try: 
        soup = BeautifulSoup ( html . read (), 'html.parser')
        meta=soup.find_all("meta")
    except:
        info=str(("In", target_website, " a parsing error occurred during scrapping in module 'soup_data_set'"))
        list_error.append(info)
        pass
    else:
        dic_scrape.update({'link':target_website})
        dic_scrape=build_dic(meta, target_website)
    return dic_scrape

    

def main():
    #ini
    list_line=[]
    cwd=os.getcwd()
    rows=[]
    columns = ['url', 'author', 'title_1', 'title_2', 'description_1', 'description2', 'duration_seg','release_date','keywords']
    df_scrapped= pd.DataFrame(columns=columns)

    if testing is True:
        filename=cwd+"/../preprocessing/test_data_ted-talks-website.csv"
        df_kaggle=first_data_set(filename)
        target_website=df_kaggle.iloc[3,5]
        df_scrapped=soup_data_set(target_website)
    else:
        filename=cwd+"/../raw_data/ted-talks-website.csv"
        df_kaggle=first_data_set(filename)
        for target_website in df_kaggle.link:
            dic_scrapped=soup_data_set(target_website)
            df_scrapped=df_scrapped.append(dic_scrapped,ignore_index=TRUE)

    df_kaggle.to_csv(cwd+'/../preprocessing/kaggle.csv') 
    df_scrapped.to_csv(cwd+'/../preprocessing/scrapped.csv') 
    np.savetxt("code_1_errors.csv", 
           list_error,
           delimiter =", ",
           newline='\n', 
           fmt ='% s')

if __name__ == '__main__':
  main()