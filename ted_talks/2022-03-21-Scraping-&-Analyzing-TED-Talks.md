---
layout: post
title:  "Scraping & Analysing  - TED Talks"
description:  "Small project to analyse TED TALK data"
date:   2022-04-05
banner_preview: blog-350-250-python-b&w-2021-04-05.jpg
banner_image: blog-1200-400-python-2021-04-05.jpg
category: Coding
tags: [python, analytics , dataengineering]
---


I wanted to find a small project of something fun to practice python web scrapping skills, SQL and Tableau. 

TED Talks is a facinating source of talks. Kaggle offers a dataset on [TED Talks](https://www.kaggle.com/datasets/ashishjangra27/ted-talks) posted on the wbsite. As a TED Talk fan, I wanted to understand the type of content available. 

<!--more-->
To follow along this project, I've made a copy of the code in this [location](https://github.com/aaas24/aaas24.github.io/tree/master/assets/post_files/2022-04-05-Scraping-&-Analyzing-TED-Talks.py)

### STEP 1 EXPLORING DATA SET

As stated above, Kaggle offers a dataset on [TED Talks](https://www.kaggle.com/datasets/ashishjangra27/ted-talks) posted on the wbsite. Loading the provided file into a SQL Server w can examine the data. 

Obtaining basic general information on the data set
```python
        info = f"""
        {'-'*40}
        # Basic data frame information
        # Num Rows: {df.shape[0]}
        # Num Column: {df.shape[1]}
        # Column Names: {df.columns.values}

        {'-'*40}
        """

        print(info)
```
```
        ----------------------------------------
        # Basic data frame information
        # Num Rows: 5440
        # Num Column: 6
        # Column Names: ['title' 'author' 'date' 'views' 'likes' 'link']

        ----------------------------------------
```

 Looking at a brief set of the data

 ```python
    print(df.head(10))
 ```

 <p align="center">
  <img src="https://github.com/aaas24/aaas24.github.io/blob/master/assets/post_files/2022-03-21-Scraping-&-Analyzing-TED-Talks/ted-talk-1.jpg" alt="Data Exploration" width="600">
</p>

From the data exploration we can see that more information on each video would be useful in order to answer the following questions: 

- Which content categories are most viewed?
- Which content categories are made available the most?
- Could the duration of the video affect the likebility of the videos?
- When was the video published? (Assuming that older videos can have more likes than newer)
- What type of evnt was this part of? WAs it a Women, or a specific location?


###  STEP 3 SCRAPPING 
    
* Fetch an example

```python
from urllib.request import urlopen
from bs4 import BeautifulSoup

html = urlopen ( "https://www.ted.com/talks/ozawa_bineshi_albert_climate_action_needs_new_frontline_leadership" ) 
soup = BeautifulSoup ( html . read (), 'html.parser')
```

* Parse the desired content

Our goal is to extract the names of the authors and their quotes, to later store them in a dictionary we can later query when we want to. 

Now we need to better analyzing the HTML tree using the prettify property. Using the property prettify (print(bsObj.prettify()), we can see (the HTML)[https://github.com/aaas24/aaas24.github.io/blob/master/assets/post_files/2022-03-21-Scraping-&-Analyzing-TED-Talks/example_html.xml]

In the HTML we can find the information we need is stord in a tag called "meta". 

```python
meta=soup.find_all("meta")
```
When we study the tag we see that in the elements inside this tag we find the information we need in the following indicies: 

|Position in the 'meta' tag|Data|
|1|url|
|27|title style 1|
|28|title style 1|
|29|description style 1|
|30|description style 2|
|33|duration in seg|
|34|keywords|
|35|release date|
|37|author|

Through some data transformation in python we are able to clean the data an obtain a new dataframe we called `df_scrapped`. To see the data cleaning process, you can look at the [code](). 

Because we included the initial `link` column from `df_kaggle`, we can join both data frames using panda merge. 

```python
df_final_raw_data=df_kaggle.merge(df_scrapped, left_on='link', right_on='link')
```

###  STEP 4 PREPROCESSING THE DATA



###  STEP 3 ANALYZING AND VISUALIZING


###  STEP 5 ML LEARNING

### CONCLUSIONS





