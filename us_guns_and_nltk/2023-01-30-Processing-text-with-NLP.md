---
layout: post
title:  "Processing text to understand Gun Issue in US"
description:  "Study guns used in mass shootings using NLP libraries"
date:   2023-01-30
banner_preview: blog-350-250-python-b&w-2021-04-05.jpg
banner_image: blog-1200-400-python-2021-04-05.jpg
category: Coding
tags: [python, dataengineering, nlp]
---

While exploring gun violence issue in the US, a dataset with the guns used in each mass shooting was found. However, as it frequently happens, the data entries are not in a way that it is immediately useful. This project aims to use neuro-processing language (NPL) libraries to analyze the data

<!--more-->


### DEPENDENCIES


PYTHON LIBRARIES

```python
    import pandas as pd
    import numpy as np
    import os
```

## Data Source: Mother Jones 

```python
df1_details=pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vQBEbQoWMn_P81DuwmlQC0_jr2sJDzkkC0mvF6WLcM53ZYXi8RMfUlunvP1B5W0jRrJvH-wc-WGjDB1/pub?gid=0&single=true&output=csv')
df1_details.info()
print('-----------------------')
print('\n')
print('\n')
df1_details.head(2)
```