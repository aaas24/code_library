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


TED Talks is a facinating source of content. Kaggle offers a dataset on [TED Talks](https://www.kaggle.com/datasets/ashishjangra27/ted-talks) posted on the website. As a TED Talk fan, I wanted to understand the type of resources available. 

<!--more-->
This project is a pretext to practice several data science techniques, including: scrapping a website, data wrangling, data classification techniques (PCA and clustering) and Machine Learning techniques.

In order to make this project managable I have divided it into several steps: 

**STEP 1** - OBTAINING DATA SET</br>
\--------------------------------------------

* Identified potential questions</br>
* Understood what gaps are in the data to answer posed questions</br>

**STEP 2** - SCRAPPING </br>
\--------------------------------------------

* Scrapped website for more information to further analyze</br>

 **STEP 3** - PREPROCESSING THE DATA</br>
\--------------------------------------------

* Transformed the dataset obtained into organized </br>
* panda Dataframes using pandas library</br>

**STEP 4** - DATA EXPLORATION</br>
\--------------------------------------------

* Applied Principal Component Analysis (PCA) to understand key columns of main dataset</br>
* Applied Clustering based on identified most important PCA's</br>
* Explored key variables: dates, duration, keywords</br>

**STEP 5** - ANALYSYS</br>
\--------------------------------------------

* Answered main posed questions</br>

**STEP 6** - ML LEARNING</br>
\--------------------------------------------

* Applied Regression Model to predict video with good performance and identified key features</br>
* Applied Natural Language Understanding techniques on descriptions to compare selection of keywords/tags used on web content</br>
</br>


To follow along this project, I've made a copy of the source code in this [Github repository.](https://github.com/aaas24/code_library/tree/main/ted_talks)
</br>
</br>
</br>
</br>
</br>
</br>
</br>

### STEP 1 - OBTAINING A DATA SET
---
***
</br>

As stated above, Kaggle offers a dataset on [TED Talks](https://www.kaggle.com/datasets/ashishjangra27/ted-talks) posted on the website. Loading the provided file into a SQL Server w can examine the data. 

Obtaining basic general information on the data set

<span style="font-size:11px"> 

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
</span>

 Looking at a brief set of the data

<span style="font-size:11px"> 

 ```python
        print(df.head(10))
 ```
</span>


 <p align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted-talk-1.png" alt="Data Exploration" width="600">
</p>

</br>
From the data exploration we can see that more information on each video would be useful in order to answer the following questions: 

- Which content categories are most viewed?
- Which content categories are made available the most?
- Could the duration of the video affect the likebility of the videos?
- When was the video published? (Assuming that older videos can have more likes than newer)
- What type of evnt was this part of? WAs it a Women, or a specific location?

</br>
</br>
</br>
</br>

###  STEP 2 - SCRAPPING 
---
***

The goal of this section is to obtain a more robust dataset than the one provided by Kaggle by scrapping the TED Talk's site. To view the entirity of the code used for this section, please visit [this link](https://github.com/aaas24/code_library/blob/main/ted_talks/3_code/code_1_scrape_data.py). 

It is important to note that througout the process of understanding the HTML and partial tweaking of the code, I stored locally the initial HTML and/or utilize samples of 1-10 links at a time with flags in the code oto avoid disrupting the site's servers while developing the code. I believe this is the code any scrapper should approach a target. 

The first step is to understand what kind of HTML we would get back and identify where we could obtain the information to answer the questions above and generate new valuable insights. 

* Fetch an example
</br>
</br>
Using one of the links provided in the Kaggle dataset obtained in Step 2, we scrape the HTML using the following code:

<span style="font-size:11px"> 

```python
        from urllib.request import urlopen
        from bs4 import BeautifulSoup

        html = urlopen ( "https://www.ted.com/talks/ozawa_bineshi_albert_climate_action_needs_new_frontline_leadership" ) 
        soup = BeautifulSoup ( html . read (), 'html.parser')
```
</span>

* Parse the desired content
</br>
</br>
Our goal is to extract the names of the authors and their quotes, to later store them in a dictionary we can later query when we want to. 

Now we need to better analyzing the HTML tree using the prettify property. Using the property prettify (print(bsObj.prettify()), we can see [the HTML.](https://github.com/aaas24/aaas24.github.io/blob/master/assets/post_files/2022-03-21-Scraping-&-Analyzing-TED-Talks/example_html.xml)

In the HTML we can find the information we need is stored in a tag called "meta". 

<span style="font-size:11px"> 

```python
        meta=soup.find_all("meta")
```
</span> 

When we study the tag we see that in the elements inside this tag we find the information we need in the following indicies: 

<span style="font-size:11px"> 
<div align="center">

|Position in the 'meta' tag|Data|
|---------|------|
|1|url|
|27|title style 1|
|28|title style 1|
|29|description style 1|
|30|description style 2|
|33|duration in seg|
|34|keywords|
|35|release date|
|37|author|

</div>
</span> 

Through some data transformation in python we are able to clean the data an obtain a new dataframe we called `df_scrapped`. To see the data cleaning process, you can look at the [code](). 

Because we included the initial `link` column from `df_kaggle`, we can join both data frames using panda merge. 

<span style="font-size:11px"> 

```python
        df_final_raw_data=df_kaggle.merge(df_scrapped, left_on='link', right_on='link')
```
</span>

The final joined data was stored in a file [here.]('https://github.com/aaas24/code_library/raw/main/ted_talks/1_raw_data/final_raw_data.csv')

</br>
</br>
</br>
</br>

###  STEP 3 - PREPROCESSING THE DATA
---
***

With a more robust dataset obtained in Step 2, we will proceed to clean and generate two base DataFrame to be used in the following steps. If you wish to see the entirity code of this code, you can visit [this Jupyter notebook.](https://github.com/aaas24/code_library/blob/main/ted_talks/2_preprocessing/ted_talks_preprocessing.ipynb)


* Create Main DataFrame

\
 With final data joined dataset, we proceed to apply data processing steps, including: 
\
        - Dropped duplicated or useless columns: 'description2', 'Unnamed: 0', 'link', 'author_y', 'title','url', 'title_1'
\
        - Converted to datetime date_recorded and date_released columns, extracting YEAR, MONTH, HOUR & MINUTES into numerical columns to be able to feed it into Machine Learning models later
\
        - Remove lists from keywords column in order to later applied get_dummies() panda function. 
        This step was particularly tricky for me. The original column looks like this: 

<span style="font-size:11px"> 

```shell
        0      ['TED', ' talks', ' climate change', ' global ...]
        1      ['TED', ' talks', ' education', ' women', ' TE...]
        2      ['TED', ' talks', ' business', ' leadership', ...]
        3      ['TED', ' talks', ' climate change', ' polluti...]
        4      ['TED', ' talks', ' climate change', ' Countdo...]
```
</span>
        The desired structure looks more like:

<span style="font-size:11px"> 

```shell
        0       'ted', 'talks', 'climatechange', 'globalissues...
        1       'ted', 'talks', 'education', 'women', 'ted-ed'...
        2       'ted', 'talks', 'business', 'leadership', 'wor...
        3       'ted', 'talks', 'climatechange', 'pollution', ...
        4       'ted', 'talks', 'climatechange', 'countdown', ...
```

</span>

\
        In order to achieve this a For loop was used to remove the list, apply lower case and remove the extra spaces in between the ''  that some words had. 

* Create dummy file

 Applied the get_dummies sunction on the new keywords2 column, which allows to apply a sum() function in a group by in order to obtain a simple count on the number of times a keyword was used across the dataset. It's also important to note that all talks have the keyword 'ted' attached to them, which provides no value overall and therefore was removed during this step. 

<span style="font-size:11px"> 

``` python
         def create_dummies_file(df):
                #converting keywords into dummy columns
                df2=df.keywords2.str.get_dummies(',')

                #joining with df
                df=pd.concat([df,df2], axis=1)
                
                #removing 'ted' column
                column_to_drop=df.columns[362]
                df2=df.drop(column_to_drop, axis=1)

                #counting dummies and creating file to rename categories
                dummy_columns=pd.Series(np.arange(15,349,1))[1:]
                df_dummies=df.iloc[:,dummy_columns].sum().reset_index()
                df_dummies.columns=['keyword', 'sum']
                df2=df_dummies.copy()
                (df2
                .groupby(['keyword'])
                .agg({'sum':'sum'})
                )
                df2=df2.sort_values(by='sum', ascending=False)
                cwd=os.getcwd()
                df2.to_csv(cwd+'/keywords.csv')
                return df
```
</span>


The result of this function is: 
1) A dataFrame 'df' with the main data structure to be later processed. 

<span style="font-size:11px"> 

||author|	views|	likes|	title|	description_1|	duration_seg|	description_2|	date_recorded_year|	date_recorded_month|	date_released_year|	...	|'water'|	'weather'|	'windenergy'|	'women'|	'womeninbusiness'|	'work'|	'work-lifebalance'|	'writing'|	'youth'|	'ted'|
|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|--|
0|	Ozawa Bineshi Albert|	404000|	12000|	Climate action needs new frontline leadership|	"We can't rely on those who created climate ch...|	834|	"We can't rely on those who created climate ch...|	2021|	12|	2022|	...|	0|	0|	0|	0|	0|	0|	0|	0|	0|	1|
Dataframe named: df     
</span >

2)  A 'keywords.csv' file containing a list of keywords and number of times it appears in the data, example: 

<div align="center">

| keyword |sum   |
|---------|------|
|'talks'  | 5440  |
| 'science'  | 1266  |
| technology'  |1200   |
|||
</div>


                
* Create Dummy DataFrame

There are 334 keywords, which we will call sub_categories of content. In order to analyze them, we need to consolidate them into bigger buckets. For that reason, I created a one:many relationship between new categories:sub_categories, in order to group the latter into bigger buckets of content that we can understand better. This categorization was done separately and stored in a file called 'keywords_categories.csv'

Utilized thus matrix, I transformed the  'keywords.csv' into a dataframe with the following structure: 

<span style="font-size:11px"> 
<div align="center">

 |       	|sub_category|	num_talks|	category|	        likes|	views|
 |--|--|--|--|--|--|
 |       0	|'3dprinting'|	9|	        technology|	        201574|	6655100|
 |       1|	'activism'|	352|	        values & emotions  |     21752759| 714057797|
 |       2|	'addiction'|	20|	        health	  |              1870500|	60982000|
 |       3|	'africa'|	197|	        global	  |              9097799|	299541000|
 |       4|	'aging'	 |       93|	        society	  |              8152092|	269034199|
 Dataframe named: df_dummies
</div>
</span>


</br>
</br>
</br>
</br>

###  STEP 4 - DATA EXPLORATION
---
***

With the two dataframes created on previous step, we proceed to apply data science techniques to undertand the dataset and explore key variables.

<span h4 style="text-decoration: underline">Principal Component Analysis (PCA)</span>


Even through the dataset is intuitively simple to understand, I wanted to practice doing a PCA analysis, which is normaly reserved for models with many variables. To do this I followed these steps: 

- Prepared the dataFrame to use by dropping all categorical columns & dummy columns from `df` and standarized the data using the sklearn.preprocessing library called 'StandardScaler'
- Used the decomposition.PA from the Sklearn library to create dataframe with components columns: 

<span style="font-size:11px"> 

``` python
        pca = decomposition.PCA()
        pca_X = pd.DataFrame(pca.fit_transform(X_std), columns=[f'PC{i+1}' for i in range(len(X.columns))]) 
```
</span>

- From `pca.explained_variance_ratio_`, we can see that the first 2 components contain almost 50% of the data"

<span style="font-size:11px"> 

``` python
        print(pca.explained_variance_ratio_)

        array([2.61155893e-01, 2.09808747e-01, 1.27262369e-01, 1.19521228e-01,
        1.01198399e-01, 9.06161518e-02, 8.05875806e-02, 9.81195975e-03,
        3.76713129e-05])
```
</span>

- Visualizing the columns on these two principal components

<span style="font-size:11px"> 

``` python
        (pd.DataFrame(pca.components_, columns=X.columns)
        .iloc[:2]
        .plot.bar()
        .legend(bbox_to_anchor=(1,1)))
```
</span>

 <p align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_pca_1.png" alt="PC1 & PC2" width="600">
</p>

<span h4 style="text-decoration: underline">Clustering</span>

1) Determining the number of lusters to use

By utilizing three separate methods of visualization, we arived at the conclusion that 4 clusters would be the best solution for this data. 

The first methos is a linear representation, nicknamed 'the elbow', as you try to search for a brear on the lines. This metgod suggests two potential cuts, one on1 or another at three but does not provide a clear answer. 

The second methos is the Silouhettes, where the shapes of the clusters do show a reasanable grouping where samples are in 4 cluesters. In this case we se that the 'bellies' of the clusters are not as pronounced as when using 2 & 3 clusters, without a significant lost in the average score. 

The third method using a dendrogram is even more clear: there is a significant increate in clusters after the 4 column. This perhaps is the clearest confirmation of our assumption 

<div class="row">
  <div class="column">
    <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_clustering_1.png" alt="Elbow Method" style="width:100%">
  </div>
  <div class="column">
    <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_clustering_2.png" alt="Silouettes Method" style="width:100%">
  </div>
  <div class="column">
    <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_clustering_3.png" alt="Dendrogram Method" style="width:100%">
  </div>
</div>

2) Assigning the clusters

<span style="font-size:11px"> 

``` python
        k9 = cluster.KMeans(n_clusters=4, random_state=42)
        k9.fit(X_std)
        labels = k9.predict(X_std)
        X.assign(label=labels)
```
</span>


3) Exploring clusters

- Determine how many values are on each cluster

<span style="font-size:11px"> 

``` python
        print(pd.Series(labels).value_counts().sort_index())

        0    1628
        1    2063
        2    1684
        3      65
        dtype: int64
```
</span>

- Describe the columns for each label

<span style="font-size:11px"> 

``` python
        (X.assign(label=labels)
        .groupby('label')
        .date_recorded_year
        .describe()
        )
```
</span>

- Describe a label in a cluster

<span style="font-size:11px"> 

``` python
        (X.assign(label=labels)
        .query('label == 0')
        .describe()
        )
```
</span>

- Visualize the means of each variable per cluster
<span style="font-size:11px"> 

``` python
        (X.assign(label=labels)
        .groupby('label')
        .mean()
        .T
        .style.background_gradient(cmap='RdBu', axis=1)
        )  
```
</span>


 <p align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_clustering_4.png" alt="Data Exploration" width="600">
</p>


4) Describing the clusters

With the information provided above, we can describe the cluester as follows: 

0 - Newer videos released in fall </br>
1 - Newer videos released in earlier in the year </br>
2 - Older videos, longer duration in seg </br>
3 - Highest views & likes


### Interesting  Visualizations

* Number of videos released per year

* Outliers of Video date_recorded_year



</br>
</br>
</br>
</br>

### STEP 5 - ANALYZING & VISUALIZING
---
***

</br>
</br>
</br>
</br>

###  STEP 6 - ML LEARNING
---
***

</br>
</br>
</br>
</br>

### CONCLUSIONS
---
***





<span style="font-size:11px"> 

``` python

        
```
</span>


 <p align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted-talk-1.png" alt="Data Exploration" width="600">
</p>

