---
layout: post
title:  "Wikipedia"
description:  "Study ways to obtain data from Wikipedia"
date:   2022-05-15
banner_preview: blog-350-250-python-b&w-2021-04-05.jpg
banner_image: blog-1200-400-python-2021-04-05.jpg
category: Coding
tags: [python, analytics , dataengineering]
---

Wikipedia is one of the most solid references for data nowadays. It is persistently updated and has become a reference in many books. I find myself constantly learning and searching it's data, so I thought it would be interesting to learn and document different methods to obtain information from it. 



# Methodology: 


Wikipdia does not allow web crawlers for downloading large number of articles. as stated in there [how-to download guide](https://en.wikipedia.org/wiki/Wikipedia:Database_download) as Wikipedia servers would not be able to cope with the constant pressure of scrapping the entire site. However, they have made available copies of the site that you can download in different formats, the easiest would be the latest copy of the state of all the pages. This will be the second method explored. 

In the case that we do hold one specific url, there are different libraries that can be explored to assist in ths job, like pandas, beautifulsoup, scrapy and more. I will focus on exploring each of these libraries as the second method explored to understand what each library has to offer. 

## Method 1: Downloading the entire Wikipedia Repository  

## Method 2: Downloading a Wikipedia Article

The article targeted is: 
article=''

### pandas library

```python
result=pd.read_html(article)
print(result)
```

### wikipedia library
This section follows the example laid by [ThePythonCode](https://www.thepythoncode.com/article/access-wikipedia-python), which uses the [wikipedia library](https://pypi.org/project/wikipedia/)

```python
import wikipedia

result = wikipedia.search(article)

#parse attributes library provides
title=result.title
summary = result.summary
categories=result.categories
content = result.content
links = result.links
references = result.references

# print info
print("Page content:\n", content, "\n")
print("Page title:", title, "\n")
print("Categories:", categories, "\n")
print("Links:", links, "\n")
print("References:", references, "\n")
print("Summary:", summary, "\n")

```
Please note that this library also supports the search function that allows you to search a term and extract the results as per the example below obtained in the thepythoncode example:

```python
result = wikipedia.search("Neural networks")
In [4]: print(result)
['Neural network', 'Artificial neural network', 'Convolutional neural network', 'Recurrent neural network', 'Rectifier (neural networks)', 'Feedforward neural network', 'Neural circuit', 'Quantum neural network', 'Dropout (neural networks)', 'Types of artificial neural networks']

# get the page: Neural network
page = wikipedia.page(result[0])
```

from here you can call the attributes title, summary, categories, etc, just like we did above



### beautiful soup library

### scrapy library

# Conclusions

## Comparing libraries to download a wikipedia page

|Library|Code||
|--|--|--|
|wikipedia||
|panda||
|beautiful soup||
|||



