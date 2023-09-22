---
layout: post
title:  "Regular Expressions Playground"
description: "Small project regarding regular expressions when parsing URLs"
date:   2021-04-08
banner_preview: blog2.jpg
banner_image: blog-banner.jpg
category: Analytics
tags: [python, analytics , dataengineering, regex]
---
 
 
One common source of user information nowadays is web traffic. Either about my personal website or throughout my career, I've found myself wanting to understand what people were doing on any particular site I was managing at the time. There are many reasons why you would want to better understand this information, from web optimization, to content generation and customer profiling; However, the purpose of this exercise is not to go in depth in analysing the behavior but rather:
 
1. To make a basic example of **URL parsing**
  
2. To utilize a python dictionary to resemble the **CASE property** available in other languages (but not in python)
  
3. To utilize **regular expressions** to extract or qualify the text form
 
<!--more-->
To follow along this project, I've made a copy of the code in this [location](https://github.com/aaas24/aaas24.github.io/tree/master/assets/post_files)
 
### STEP BY STEP PROJECT
 
* STEP 1 FINDING A DATASET
 
The data used for this study was originally downloaded from [Moz Website](https://moz.com/top500), which offered a free list of the most popular 500 websites on the internet. I believe nowadays this list is no longer available.
 
I found it hard to locate synthetic data that emulates a web visit to a site. 
 
* STEP 2 ANALYZING THE DATA
 
####  Defining main program logic to cover all objectives
 
The main program is meant to have a CASE like property, which will be called "***Switcher***". It will be using a dictionary to map to different modules. This will set up the main function of the program as follows:

 ``` python
   def main():
   all_URLs= readFile()
   for URL in all_URLs:
       i= identify_i(URL)
       switcher={
               0:case0(URL),
               1:case1(URL),
               }
       switcher.get(i,'Invalid')
       save_in_doc()
```
 
The regular expressions will be used in the parsing done under each case.
 
###  Read file
 
This function is fairly straightforward as we is the open function os the cvs library to read and then add each line to a list called "***all_URL***"
 
###  Define which type of URL we have
 
We now proceed to "clean" the url from any parameters to avoid the chance of having dirty values that could confuse the regular expression.
 
Once the parameters are stripted, we use regex library (re) to identify the type of URL we have: with protocols or without protocols. For example:

 ``` python 
   regex=re.compile(r"(?P<protocol>(:\/\/))")
   if regex.match(URL) != "":
       i = 0
       dic_URL.update({'Comments':i})
       return i, URL
```
 
If we look specifically at the line:
 
  ` r"(?P<protocol>(:\/\/))"`
 
When we analyze the re in an online website such as [Regex101.com](https://regex101.com) we get:
 
| r | prefix to a string indicates that the string is a raw string |
|-|-|
| <protocol> | Named Capture Group protocol|
| ():\/\/)) | where : matches the character : literally (case sensitive)
\/ matches the character / literally (case sensitive)
\/ matches the character / literally (case sensitive) |
 
 
This means that for the example "https://www.apple.com", the regex would identify the "://" as existing, which therefore would be different then ***empty*** when we apply the ***match*** property in the second line of the code file [code.py](docs/CONTRIBUTING.md).
 
Through this expression, and the subsequent regular expression in the code, we are able to assign a value to the variable "***i***". If there is a "***://***" match, then the value i=0, if not, i=1.
 
###  Parse
 
Now that we have a value "i" found in the section above, we can see that the "switcher" points to two values:key pairs. 0:case0() and 1:case1(). If we retrieve the definition of each of the "case" functions, we will have examples of the type of URLs each module is set to parse. For example:
 
   `print(case0.__doc__)`
 
outputs:
 
   This function parses URL with a structure similar to the following examples:
   https://www.reverbnation.com | https://www.apple.com/shop/buy-mac/pro_13_inc?q=search | file://localhost:4040/zip_file
   This function extracts the following information from the URL:
       *) the protocol, which is any value before "://". In the second example: https
       *) the domain, which is the first value after the protocol was removed. In the second example: www.apple.com
       *) the last page, which is the last value after the protocol was removed. In the second example: pro_13_inc
       *) the first page, which is the first value after the domain. In the second example: buy_mac
 
Parsing the URL is done with a simple *split* function:
 
  ` URL=URL.split('://')`
 
The resulting list can then be assigned to different variables, like the example below:
 
 ``` python 
   domain= URL[0]
   lastPage= URL[-1]
   firstPage= URL[1]
 ```

This is where list notation in python saves us a lot of time compared to my previous excel sheets where I had to apply multiple layers of "If" to understand which cell contained the last value.
 
Finally, with all values extracted, we update the dictionary that holds the information of the URL being analyzed:
 
   `dic_URL.update({'Protocol':protocol,'Domain':domain,'Last Page':lastPage, "First Page": firstPage})`
 
###  Write
 
Similarly to the function for reading, this function is fairly straightforward thanks to the built-in function *DictWriter*, which writes a python dictionary into comma separated file format.
 
 
### CONCLUSIONS
 
Given that this exercise had three different objectives (1- practice parsing, 2- use *CASE* property version and 3-use regular expressions),  the resulting code is not the most simplified and has redundancies when parsing the URL. However, it is a fun exercise for me as I was able to do in fewer lines what would take many excel columns to achieve. I also acknowledge that there is very little error handling added and should be part of a code review in the future.
 
While doing this project I found it hard to locate synthetic data that emulates organic web traffic to a site. In order to pay it forward, I have made available the data I found, limited as it is.
 
In the past, my mentor at the time, created synthetic data with a python library. I  plan to create some synthetic data in the future that can help testing this code to ensure most cases are falling within the expected code. I will make that synthetic code available as well.
