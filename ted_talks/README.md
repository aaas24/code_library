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

* Transformed the dataset obtained into organized panda Dataframes using pandas library</br>

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

# STEP 1 - OBTAINING A DATA SET
---
***
</br>

 As stated above, Kaggle offers a dataset on [TED Talks](https://www.kaggle.com/datasets/ashishjangra27/ted-talks) posted on the website. The data has been uploaded to a dataframe. 

We can obtain a general information of it. 

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
From this general view, we can immidiately ask some general questions, like: 

- Which are the most viewed videos?
- Who are the most viewed authors?
- Is there a sustancial difference between liked and viewed?. If so, which are the top videos on each?

However, some other interesting questions can be: 

- Which content categories are most viewed?
- Which content categories are made available the most?
- Could the duration of the video affect the likebility of the videos?
- When was the video published? (Assuming that older videos can have more likes than newer)
- What type of event was this part of? Was it a Women, or a specific location?

</br>
To answer some of these questions, the current data set is insufficient. However, this information may be available on each of the video's website. This poses the opportnity to extract the data using a targeted web scrapping techbique. 
</br>
</br>
</br>
</br>

#  STEP 2 - SCRAPPING 
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

#  STEP 3 - PREPROCESSING THE DATA
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

#  STEP 4 - DATA EXPLORATION
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

- Visualizing the columns in the first two principal components

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

1) Determining the number of clusters to use

By utilizing three separate methods of visualization, we arived at the conclusion that 4 clusters would be the best solution for this data. 

The first methos is a linear representation, nicknamed 'the elbow', as you try to search for a brear on the lines. This metgod suggests two potential cuts, one on1 or another at three but does not provide a clear answer. 

The second methos is the Silouhettes, where the shapes of the clusters do show a reasanable grouping where samples are in 4 cluesters. In this case we se that the 'bellies' of the clusters are not as pronounced as when using 2 & 3 clusters, without a significant lost in the average score. 

The third method using a dendrogram is even more clear: there is a significant increate in clusters after the 4 column. This perhaps is the clearest confirmation of our assumption 


<div align="center">

|Elbow Method|Silouettes Method|Dendrogram Method|
|---------|------|-----|
|<img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_clustering_1.png" alt="PC1 & PC2" width="100%"> | <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_clustering_2.png" alt="PC1 & PC2" width="100%"> |<img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_clustering_3.png" alt="PC1 & PC2" width="100%">|
|||
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

</br>
</br>

# STEP 5 - ANALYZING & VISUALIZING
---
***

When we first obtained the data we posed some questions, now is time to find the answers to them and other new ones. It's important to remember that this analysis is based on the 5440 videos obtained and may not correspond to the complete offering in the Ted Talk website and that, as such, may also not aggregate the data from their other media channels like their podcasts & tv channels. 

</br>
</br>

- Which are the most liked videos?

<div align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_analysis_1.png" alt="Data Exploration" width="100%">
</div>

- Which are the most liked authors?

<div align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_analysis_4.png" alt="Data Exploration" width="50%">
</div>


- Is there a sustancial difference between liked and viewed?. If so, which are the top videos on each? 

There is a direct correlationship between the variables liked and views, as shown in the graph below: 
<div align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_analysis_2.png" alt="Data Exploration" width="100%">
</div>


## What year were these talks recorded?


* The majority of the videos were recorded the last 20 years

 <p align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_exploration_recorded_year.png" alt="Data Exploration" width="70%">
</p>

* However, we see some outliers of video date_recorded_year variable from 1970-2000
<div align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_exploration_outliers_date_recorded.png" alt="Data Exploration" width="50%">
</div>

</br>
</br>

## Which content categories are most viewed?

</br>
</br>

* Main Content Categories

<div align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_exploration_key_categories.png" alt="Data Exploration" width="70%">
</div>

* Main Content Sub-Categories

<div align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_exploration_key_subcategories.png" alt="Data Exploration" width="70%">
</div>

</br>


- Could the duration of the video affect the likebility of the videos?

<div align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_ted_talks_analysis_3.png" alt="Data Exploration" width="100%">
</div>

Interestingly enough, in most years the majority of the videos liked stay below the first 1000sec (16min40sec). However, in 2020 one can see a lot more liked videos that are far longer, reaching ~4000sec (1hr 46min). This may be explained by the worldwide lockdowns during the COVID-19 pandemic, when people were stuck at home with few new streaming content options. In that context, it is likely people were more willing to spend more time on ted talks than the previous year.


<div align="center">

|Elbow Method|Silouettes Method|
|---------|------|
|<img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_analysis_6.png" alt="2019" width="100%"> | <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted_talks_analysis_7.png" alt="2020" width="100%"> |
</div>

</br>
</br>
</br>
</br>

###  STEP 6 - ML LEARNING
---
***
#### *A) Predicting model for if a video will perform well:*
<br>
The goal is to predict a "good performance" for a given video, when we are defining 'good performance' as at least 75% percentile. 

We run 4 different models: 

|Model|Y_Prediction|
|--|--|
|Logistic Regression|0.56|
|Simple Tree|0.59|
|Random Forest|0.64|
|X-Boost|0.68|

Based on the Best Performing Models "XG-Boost", the key features are: 

<br>
- Date related variables, whre we can see that for well performing videos: 

* there were more videos performing better with 5 min duration. Underperforming videos tended to last longer
* Well performing videos tended to be released during spring

<br>
- Keywords related to: 

* Personal Growth: personality, goals, motivation, collaboration, communication, humanity, self, performance, creativity
* Work: business, work-life balance , productivity, 
* Global issues: culture, politics, climate change, planets, gender, virus
* Other topics: music, sports, philosophy, art, health
</br>
#### Models
To be able to utilize the models below, the data must be clean of NaNs, numerical, balanced, standarized and split into training, test and validation. In this section we show the steps in code we utilized to achiev the state used for the models. 

Note: For readibility purposes we show the output of Jupyter notebook staring with ">"

<span style="font-size:11px"> 

``` python
#verifying no NAN in data feeding model
df[df.likes.isnull()==True]

>  0 rows × 363 columns 

#define target

#we define TARGET a well performing video if it is above 75% percentile. So the model should predict if a video will#perform above 75% percentile
threshold= np.percentile(df.likes, 75)

#create target column
df['target']=[1 if x>threshold else 0 for x in df.likes]

#drop multicolinearity columns
data=df.drop(['likes', 'views'], axis=1)

#drop text columns
data=data.drop(['author', 'title', 'description_1', 'description_2', 'keywords2'], axis=1)

#Balance data
data.target.value_counts()
> 0    4098
1    1342
Name: target, dtype: int64

positive_labels = data[data.target==1]
num_positive_labels = positive_labels.shape[0]
num_positive_labels
>1342

negative_labels = data[data.target==0].sample(num_positive_labels)
negative_labels.shape
>(1342, 357)

balanced_data =  positive_labels.append(negative_labels)
balanced_data.target.value_counts()
>1    1342
0    1342
Name: target, dtype: int64

## Splitting data into test splits
y = balanced_data.pop('target')
X = balanced_data

X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size = 0.3)
X_valid, X_test, y_valid, y_test = train_test_split(X_valid, y_valid, test_size = 0.33)
```
</span>


##### Logistic Regression
<span style="font-size:11px"> 

``` python
# fit a model
clf = LogisticRegression(penalty='l2').fit(X_train, y_train)
# predict probabilities
pred_reg = clf.predict_proba(X_test)[:, 1]
        
```
</span>

##### Decision Tree
##### Random Forest
##### XGBoost

##### Comparing Models
</br>
</br>
</br>

### CONCLUSIONS
---
***

Areas of improvements:
1) More information on the authors. Understanding age, gender and nationality of authors, may answer questions related to diversity of the speakers. This data could be parcially scrapped from Wikipedia as there is a dedicated website that tracks this information. 
https://en.wikipedia.org/wiki/List_of_TED_speakers

Other questions we could not answer: 

- What type of event was this part of? Was it a Women, or a specific location?
- Which content categories are made available the most?

<span style="font-size:11px"> 

``` python

        
```
</span>


 <p align="center">
  <img src="https://github.com/aaas24/code_library/raw/main/ted_talks/images/ted-talk-1.png" alt="Data Exploration" width="600">
</p>
