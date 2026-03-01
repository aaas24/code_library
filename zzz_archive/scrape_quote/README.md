---
layout: post
title:  "Scraping Website - Quote of the day"
description: "Small project using a quotes website to scrape quote database and allow text search"
date:   2020-04-05
banner_preview: blog2.jpg
banner_image: blog-banner.jpg
category: Python
tags: [python, analytics , dataengineering]
---

## DESCRIPTION

This project is a step by step of several attempts to master webscraping. Given that the practices is not always ethical, I have limited the studies to websites that either allow the practice in their robot.txt web file or that allow the practice, like: http://toscrape.com

I wanted to find a small project of something fun to practice python web scrapping skills and I thought of the many times a good quote would be useful to have at hand. I thought of starting of by building a base pool of famous quotes, which I could search, enrich and filter. The particular project defined here uses the Quotes website of http://toscrape.com as a baseline. 

This project is also based off the book "Web Scraping with Python: Collecting Data from the Modern Web" [1]


REFERENCES
[1] Mitchell, Ryan. Web Scraping with Python: Collecting Data from the Modern Web (Kindle Location 70). O'Reilly Media. Kindle Edition. 


<!--more-->

{% include image_full.html imageurl="/assets/images/blog-detail.jpg" title="Blog Desc" caption="Blog Image Desc" %}

### STEP BY STEP PROYECT

* STEP 1 CHOSSING A WEBSITE 

Web scraping is an ethically debated practice. Many articles online argue what are the greylines and, although the purpose of this post is not to go deep into that discussion, it is something I had to evaluate when considering what to use in my practice. Luckly, the tech community has many valuable open assets. One that I found was the website: http://toscrape.com, which has a particular website for quotes, as it clearly states it: 

> “A website that lists quotes from famous people. It has many endpoints showing the quotes in many different ways, each of them including new scraping challenges for you, as described below.” 

* STEP 2 SET UP ENVIRONMENT

####  Creating python environment
    virtualenv test_scraping

#### activate the environment "test_scraping"
    . /Users/alialvarez/opt/anaconda3/bin/activate && conda activate /Users/alialvarez/opt/anaconda3/envs/test_scraping; 

#### to deactivate the environment
    conda deactivate

#### install needed packages
    sudo pip install beautifulsoup4


STEP 3 SCRAPPING 
    
#### Fetch the content (should be done once)

```
from urllib.request import urlopen
from bs4 import BeautifulSoup

html = urlopen ( "http://quotes.toscrape.com" ) 
bsObj = BeautifulSoup ( html . read (), 'html.parser')
```

#### Parse the content

Our goal is to extract the names of the authors and their quotes, to later store them in a dictionary we can later query when we want to. 

Now we need to better analyzing the HTML tree using the prettify property. Using the property prettify (print(bsObj.prettify()), we can see the HTML:

```
<div class="row">
    <div class="col-md-8">
     <div class="quote" itemscope="" itemtype="http://schema.org/CreativeWork">
      <span class="text" itemprop="text">
       “The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking.”
      </span>
      <span>
       by
       <small class="author" itemprop="author">
        Albert Einstein
       </small>
       <a href="/author/Albert-Einstein">
        (about)
       </a>
      </span>
      <div class="tags">
       Tags:
       <meta class="keywords" content="change,deep-thoughts,thinking,world" itemprop="keywords"/>
       <a class="tag" href="/tag/change/page/1/">
        change
       </a>
       <a class="tag" href="/tag/deep-thoughts/page/1/">
        deep-thoughts
       </a>
       <a class="tag" href="/tag/thinking/page/1/">
        thinking
       </a>
       <a class="tag" href="/tag/world/page/1/">
        world
       </a>
      </div>
```
In the HTML we can find the authors associated to the <small> tag with the class "author", while the quotes are associated to <span> with the class "text". Using the BeautifulSoup object, we are able to extract both. 

   content=bsObj2.findAll(tag,{"class":tagclass})

where, for authors the tag=small and the tagclass=author, whereas for the quotes tag=span and tagclass=text.  

In the code, I have created two simple functions: one to create the lists with the tag values cleaned and stripped from all tags but the text, and the other to merge both lists, the authors and the quotes, into a dictionary. These functions look like this: 

```
def tag_list(tag,tagclass):
    """
    This function extracts the list of tags and returns the list
    """
    bsObj2=bsObj
    a=[]
    content=bsObj2.findAll(tag,{"class":tagclass})
    for item in content:
        a.append(item.get_text())
    return a


def merge_lists(list1,list2):
    """
    This function ebuilds and returns a dictionary constructed on merging two lists
    """
    newDic = {list1[i]: list2[i] for i in range(len(list1))}
    return newDic
```
Now, it's just a matter of calling the values and printing the result: 

```
authorList= tag_list("small","author")
quotesList= tag_list("span","text")
quotesDic= merge_list(authorList,quotesList)
print(quotesDic)
```

The resulting dictionary can be converted into a data frame with the panda library and query easily. Moreover, more data can me added later. 

### CONCLUSIONS

Although this is a simple project, it was a great introduction to the BeautifulSoup library and helped poised questions. 

In more robust scenarios, it would be interesting to build something that can handle server errors and allow users to test the tags with simple inputs. this would also require error handling on the data provided by the users, but it shows the wonderful possibilities that this proyect has for future questions. 

Sense I worked with quotes, I am sharing my favorite one from this little project:

> “I have not failed. I've just found 10,000 ways that won't work.”” 
> <cite>― Thomas A. Edison</cite>



