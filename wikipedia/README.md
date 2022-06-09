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
Wikipedia does not allow web crawlers for downloading large number of articles. as stated in there [how-to download guide](https://en.wikipedia.org/wiki/Wikipedia:Database_download) as Wikipedia servers would not be able to cope with the constant pressure of scrapping the entire site. However, they have made available copies of the site that you can download in different formats, the easiest would be the latest copy of the state of all the pages. This will be the second method explored. 

In the case that we do hold one specific url, there are different libraries that can be explored to assist in ths job, like pandas, beautifulsoup, scrapy and more. I will focus on exploring each of these libraries as the second method explored to understand what each library has to offer. 

To get a full code view on this project, please see this [Jupyter Notebook](https://github.com/aaas24/code_library/tree/main/wikipedia/wikipedia.ipynb). 

**Disclaimer**: I tried running all commands from the Jupyter notebook in an effort to test its capabilities, expand my knowledge on libraries, increase traces of code changes and reduce switching between tools. This may have resulted in other inefficiencies that can be solved by directly running scripts. In order to run shell commands I utilized this function: 

```python
    import subprocess

    def runcmd(cmd, verbose = False, *args, **kwargs):

        process = subprocess.Popen(
            cmd,
            stdout = subprocess.PIPE, 
            stderr = subprocess.PIPE,
            text = True, 
            shell = True
        )
        std_out, std_err = process.communicate()
        if verbose:
            print(std_out.strip(), std_err)
        pass
```

**Example:**

```
    runcmd("echo 'Hello World'", verbose = True)
```

## Method 1: Downloading the entire Wikipedia Repository 

### Core libraries used: 

<span style="font-size:11px"> 

```python
    import pandas as pd
    import numpy as np
    import os
```
</span>

### Downloading Dump

<span style="font-size:11px"> 

```python
    # deletes previous file
    try:
        os.remove(filename)
    except OSError:
        pass

    # download latest wiki dump 
    runcmd("wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2", verbose = True)
```
</span> 

### Decompressing Dump

<span style="font-size:11px"> 

```python
    # decompress file using #wikiextractor library
    runcmd("bzip2 -d /Users/alialvarez/Desktop/STUDIES/github/code_library/wikipedia/enwiki-latest-pages-articles.xml.bz2", verbose = True) 
```
</span>

### Obtaining Metadata with [Wiki Dump Parser Library](https://github.com/Grasia/wiki-scripts/tree/master/wiki_dump_parser)

<span style="font-size:11px"> 

```python
    try:
        os.remove(filename[:-8]+'.csv')
    except OSError:
        pass


    import wiki_dump_parser as parser
    parser.xml_to_csv('enwiki-latest-pages-articles.xml')
```
</span> 

The resulting file shown below has several failed parsed rows while processing the text columns [page_title & contributor_name] that make it hard to utilize directly. However, with some data wrangling, one would think it could be possible to obtain a curated list of the page_id's and titles. However, it would be an interesting exercise to understand if one of the dump files contains this data pre-arranged, namely the "enwiki-****-all-titles.gz"

 <p align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/wikipedia/images/wiki_1.png" alt="Metadata Example" width="600">
</p>

### Obtaining Markup text with [Wiki Dump Reader library](https://github.com/CyberZHG/wiki-dump-reader)

<span style="font-size:11px"> 

```python
    from wiki_dump_reader import Cleaner, iterate

    wiki={}
    cleaner = Cleaner()

    for title, text in iterate('enwiki-latest-pages-articles.xml'):
        orig_text=text
        text = cleaner.clean_text(text)
        cleaned_text, links = cleaner.build_links(text)

        #add files to dictionary
        wiki.update({title:[cleaned_text]})

    #create DataFrame and export it as CSV
    df_wiki=pd.DataFrame.from_dict(wiki, orient='index')
    df_wiki.columns=['cleaned']
    df_wiki.to_csv(os.path.join(os.getcwd(), 'wiki_dump_example.csv'))
```
</span> 

The code above results in a clean file with many redirects rows, like this:  

 <p align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/wikipedia/images/wiki_2.png" alt="Metadata Example" width="600">
</p>

One potential improvement is to delete this REDIRECTS and, when failing to find a term, utilize the "enwiki-****-redirects.gz" file provided as part of the dumps to find a different title page


## Method 2: Downloading a Wikipedia Article

The article targeted is: 
article=''

### pandas library

<span style="font-size:11px"> 

```python
result=pd.read_html(article)
print(result)
```
</span> 

### wikipedia library
This section follows the example laid by [ThePythonCode](https://www.thepythoncode.com/article/access-wikipedia-python), which uses the [wikipedia library](https://pypi.org/project/wikipedia/)

As an example of how this works, we will be searching for pages/content related to "ted talk speakers", related yo our [ted talk project](https://github.com/aaas24/code_library/raw/main/ted_talks), hence: 

``` 
subject='ted talk speakers' 
```

#### Search

<span style="font-size:11px"> 

```python

    # To obtain a search on the subject:
    import wikipedia

    search_result = wikipedia.search(subject)
    print('the search result is:')
    print(search_result)
    result=search_result[1]
    print('')
    print('the selected page is:', result)
```
</span> 

<span style="font-size:11px"> 

```python
    # to obtain a URL base on the search result
    url=(result).replace(" ", "_")
    url= 'https://en.wikipedia.org/wiki/'+ url

    print(url)
</span> 

#### Obtain Article Information



from here you can call the attributes title, summary, categories, etc, just like we did above


### BeautifulSoup library

### scrapy library

# Conclusions

## Comparing libraries to download a wikipedia page

|Library|Code||
|--|--|--|
|wikipedia||
|panda||
|beautiful soup||
|||



<span style="font-size:11px"> 

```python

```
</span> 