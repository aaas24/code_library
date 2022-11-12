Gun violence in the United States goes beyond school shootings, but the defenseless of young kids, in environments that are meant to keep them safe takes this situation beyond any norm. As a mother and a citizen, I worry of the gun violence in the United States. Given my skills in data analytics, I gravitated towards trying to make sense of this senseless violence, in the hope to have better discussions and, hopefully, share some light into this issue. 

## Summary findings

- Num of incidents has steadily increased decade vs decade, but they have become more deadly (fatality vs gun victims) in the last 10 years. We can speculate this is due to the use of automatic weapons, but no data is available to proof

- The largest numbers of incidents have happen in Highschools, particularly in January

- The states with the highest number of fatalities are: 
        ['California',
        'Virginia',
        'Texas',
        'Connecticut',
        'Florida',
        'Colorado',
        'Pennsylvania',
        'Washington',
        'Minnesota',
        'Oregon']
- Although California and Texas have the largest number of incidents, Virginia and Connecticut have most deadly shootings registered.

To view this book, you can see the the [Jupyter Notebook code](https://github.com/aaas24/code_library/blob/main/school_shootings/SchoolSchootings_vfinal.ipynb).

## Data Sets Sources
|Dataset Name|Owner/Credit|Description|
|--|--|--|
|[school-shooting-data](https://github.com/ecodan/school-shooting-data)|[Ecodan-github](https://github.com/ecodan)|Munge of the dataset underlying the Pah/Amaral/Hagan research ([https://news.northwestern.edu/stories/2017/01/shootings-us-schools-link-unemployment]) on school shootings with the Wikipedia article ([https://en.wikipedia.org/wiki/School_shootings_in_the_United_States]) from 1990 to present.|


## Visualization Style
Seaborn library has a out-of-the-box set for five-thirty-eight styling of visualization that can be used with the simple command: 

```python
import seaborn
style.use('fivethirtyeight')
```

The style of the visualizations is similar to: 

 <p align="center">
  <img src="https://github.com/aaas24/code_library/blob/main/school_shootings/images/image1.png" alt="Example Graph" width="600">
</p>

The styling of these graphs include: 

plt.text for title, subtitle and footer, Ex: 

```python
x=0.5 #Modify to manipulate start position of text versus margin
title='Fatalities Registered per Month'
subtitle='Highschool incidents are disproportionally more common in January'
x_var='month'
y_var='count_shootings'
num_blanc_spaces=25

###Title 
plt.text(x=-x, y=data[y_var].max()+10, 
              s=title, 
              fontsize=26, weight='bold', alpha=.85
              )
### Subtitle
plt.text(x=-x, y=data[y_var].max()+5, 
              s=subtitle, 
              fontsize=19, alpha=.85
              )
### Footer
num_spaces=" ".join(" "*int(num_blanc_spaces))
plt.text(x=-x, y=-10, 
              s=footer_left+num_spaces+footer_right,
              fontsize=17,
              color="#f0f0f0",
              bbox=dict(facecolor="black", alpha=0.5)
              )
plt.show()
```

Other styling details include: 

- Adding line in X `plt.axhline(y=0, alpha=0.7, linewidth=1.5, color='black')`

- Making axis easier to read: 

```python
ax.set(xlabel=None)
plt.ylabel(y_var.replace("_"," ").capitalize())
plt.tick_params(axis='both', which='major', labelsize=18)
```


## Improvements
 Forecast shootings for current decade to compare with past ones. 



