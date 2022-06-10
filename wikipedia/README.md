---
layout: post
title:  "Wikipedia"
description:  "Study ways to obtain data from Wikipedia"
date:   2022-05-15
banner_preview: blog-350-250-python-b&w-2021-04-05.jpg
banner_image: blog-1200-400-python-2021-04-05.jpg
category: Coding
tags: [python, dataengineering, re]
---

Wikipedia is one of the most solid references for data nowadays. It is persistently updated and has become a reference in many books. I find myself constantly learning and searching it's data, so I thought it would be interesting to learn and document different methods to obtain information from it. 

This project studies downloading the entire wikipedia data and how to quickly obtain a single article information. 

As a summary, here is my assessment of the libraries used: 

1=Least -> 5= Most

**For all data dump:**
|Concept|Wiki Dump Parser|Wiki Dump Reader
|---------|------|------|
|Ease to install|4|4|
|Ease to use|4|4|
|Output Value|3|5|
|||

</br>

**For a Single article:**
|Concept|Wikipedia|BeautifulSoup|Pandas|
|---------|------|------|------|
|Ease to install|4|3|5|
|Ease to use|5|3|5|
|Flexibility|4|5|3|
|||

</br>
</br>

CONTENT

[METHOD 1: DOWNLOADING ALL WIKIPEDIA](#method1) </br>
[METHOD 2: DOWNLOADING SINGLE WIKIPEDIA ARTICLE](#method2) </br>
[WIKIPEDIA LIBRARY](#wiki) </br>
[BEAUTIFULSOUP](#bs) </br>
[PANDAS](#pd) </br>
</br>
# Methodology: 
Wikipedia does not allow web crawlers for downloading large number of articles. as stated in there [how-to download guide](https://en.wikipedia.org/wiki/Wikipedia:Database_download) as Wikipedia servers would not be able to cope with the constant pressure of scrapping the entire site. However, they have made available copies of the site that you can download in different formats, the easiest would be the latest copy of the state of all the pages. This will be the second method explored. 

In the case that we do hold one specific url, there are different libraries that can be explored to assist in ths job, like pandas, beautifulsoup and more. I will focus on exploring each of these libraries as the second method explored to understand what each library has to offer. 

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

## <a name="method1"> Method 1: Downloading the entire Wikipedia Repository  </a> 
---

### Core libraries used: 

<span style="font-size:11px"> 

```python
    import pandas as pd
    import numpy as np
    import os
```
</span>

### Downloading & Decompressing Dump

This section requires having the following dependencies in your shell: 
- wget
- bzip2


<span style="font-size:11px"> 

```python
    # deletes previous file
    try:
        os.remove(filename)
    except OSError:
        pass

    # download latest wiki dump 
    runcmd("wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2", verbose = True)

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

</br>
</br>

## <a name="method2"> Method 2: Downloading a Wikipedia Article </a>
---

The article targeted is: 
article=''

### <a name="wiki"> A) wikipedia library </a>
This section follows the example laid by [ThePythonCode](https://www.thepythoncode.com/article/access-wikipedia-python), which uses the [wikipedia library](https://pypi.org/project/wikipedia/). As an example of how this works, we will be searching for pages/content related to "ted talk speakers", related yo our [ted talk project](https://github.com/aaas24/code_library/raw/main/ted_talks), hence: 

<span style="font-size:11px"> 

```python  
    subject='ted talk speakers' 
```
</span> 

#### **Search**

<span style="font-size:11px"> 

```python

    # To obtain a search on the subject:
    import wikipedia

    search_result = wikipedia.search(subject)
    print('the search result is:')
    print(search_result)
    result=search_result[1] # this selects the first option of the tuple, which is the desired outcome in our case. You need to adapt this to your use case 
    print('')
    print('the selected page is:', result)
```
</span> 

 <p align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/wikipedia/images/wiki_3.png" alt="Search" width="600">
</p>

To obtain a URL base on the search result

<span style="font-size:11px"> 

```python
    url=(result).replace(" ", "_")
    url= 'https://en.wikipedia.org/wiki/'+ url
    print(url)
```
</span> 

#### **Article Information**

Once you obtain the targeted URL, you can call the attributes title, summary, categories, etc.

<span style="font-size:11px"> 

```python
    result=wikipedia.page(result)

    #parse attributes library provides
    title=result.title
    summary = result.summary
    categories=result.categories
    content = result.content
    links = result.links
    references = result.references
    html=result.html()

    # print info
    print("Page content:\n", content, "\n")
    print("Page title:", title, "\n")
    print("Categories:", categories, "\n")
    print("Links:", links, "\n")
    print("References:", references, "\n")
    print("Summary:", summary, "\n")
```
</span> 

For an example of the outputs, this [notebook](https://github.com/aaas24/code_library/blob/main/ted_talks/4_enhance_authors/Authors.ipynb)


### <a name="bs"> B) beautifulSoup library</a>

The first step is obtaining the html: 

<span style="font-size:11px"> 

```python
    from bs4 import BeautifulSoup
    from urllib.request import urlopen


    html = urlopen (url)
    bsObj = BeautifulSoup(html.read (), 'html.parser')
    print(bsObj)
```
</span> 

Once we obtain the html code of the target website, we can use different methods to extract the parts of the text we wish to obtain.

**B.1) The first method is using the findAll function in BeautifulSoup Library:**

<span style="font-size:11px"> 

```python
    def tag_list(tag):
        """
        This function extracts the list of tags and returns the list. It uses the findAll function of BeautifulSoup
        """
        soup=bsObj
        a=[]
        content=soup.findAll(tag)
        for item in content:
            a.append(item.get_text())
        return a
```
</span> 

For example, if we wanted to extract a list of authors from this html: 

<span style="font-size:11px"> 


```python
    authors= (tag_list("td")
            [6:] #remove first 6 values that do not correspond to authors or talks
            )
```
</span> 

 <p align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/wikipedia/images/wiki_4.png" alt="Authors Example" width="600">
</p>


**B.2) The second method is using Regular Expressions**

<span style="font-size:11px"> 

```python
    import re
        
    #Parse HTML to find urls of speakers 
    txt = str(bsObj)
    result=[]
    reg='(?<=td>)(.*)(?=</td>)'

    reobj = re.compile(reg)
    for matchobj in reobj.finditer(txt):
        result.append(matchobj[1 ])

    for line in result:
        print (line) 
```
</span> 


For a more detailed example on regex use, please see this [notebook](https://github.com/aaas24/code_library/blob/main/ted_talks/4_enhance_authors/Authors.ipynb)

### <a name="pd">  C) pandas library</a>

It's almost obvious but still important to call out how easy panda makes this: 

<span style="font-size:11px"> 

```python
    html=pd.read_html(url)

    print(type(html))
    print(html)
```
</span> 


# Conclusions

## On downloading entire wikipedia

The Wiki Dump Parser Library is very easy to utilize but the output requires further transformations as it does not correctly parses the text fields. If you require the ID or titles alone, it might be available on one of the file dumps released by wikipedia. However, for basic stats like bits or contributor name, it seems like a good start. 

The Wiki Dump Reader provides a great markup result for a fast understanding of each article and could be fed into a ML model with ease. 

## On downloading an article

The Wikipedia library is by far the most easy and robust to use to connect to the wikipedia API. However, since it pre-processes the output, BeautifulSoup offers more flexibility when targeting specific sections (such as tables). 

BeautifuSoup is very powerful as it allows to target tags along all the html. However, it is not as easy to use because it is not a stand-alone package but rather requires the use 'requests' and some understanding of html & CSS. 

Pandas out of the box read_html is convenient and easy to use. It provides a list of elements that can be cycled through quickly making it both simple and fast. 

### Comparing libraries to download a wikipedia article


1=Least -> 5= Most

|Concept|Wikipedia|BeautifulSoup|Pandas|
|---------|------|------|------|
|Ease to install|4|3|5|
|Ease to use|5|3|5|
|Flexibility|4|5|3|


# Improvements

- Include scrapy in comparison. This would be used in the case you would be targeting several website within wikipedia without exceeding a large number of articles that can risk infringing their policies. 

- Compare output "enwiki-****-all-titles.gz" with Wiki Dump Parser Library

- Delete this REDIRECTS and, when failing to find a term, utilize the "enwiki-****-redirects.gz" file provided as part of the dumps to find a different title page