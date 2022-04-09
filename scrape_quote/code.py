from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.error import HTTPError, URLError

#--- HANDLING ERROR IN SERVER
try:
    html = urlopen ( "http://quotes.toscrape.com/" ) 
except HTTPError as e:
    print(e)
except URLError as e:
    print("The server could not be found")

#--- SCRAPPING
bsObj = BeautifulSoup ( html . read (), 'html.parser')


#--- EXTRACTING TAGS
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

authorList= tag_list("small","author")
quotesList= tag_list("span","text")
quotesDic= merge_lists(authorList,quotesList)
print(quotesDic)

## --- This section is in case tag and class should be provided by an user, instead of written in the code: 
# data = input("Insert tag & to be search for separated by comas. Ex: span,author ").split(',')

# if data[0] == "":
#     exit()

# if len(data)==1:  
#         contentList= bsObj.findAll(data)
#         print (contentList)  
# else:       
#     tagClass[data[0]] = data[1]
#     for tagName,tagAttribute in tagClass.items():
#         contentList= bsObj.findAll(tagName, {"class":values})
#         print (contentList)  


## --- Storing information in text file

# a=str("content.txt")
# with open(a, "w") as f:
#     f.write(str(bsObj))
#     f.close()

# f2 = open(a,'r')
# line = f2.readline()
# while(line!=""):
#     # print(line)
#     line = f2.readline()
# f2.close()


### --- WORKING CODE & NOTES 
# '''' WHERE YOU LEFT OFF
#

# '''' REUSABLE CODES
# # git commit -am "Reformatting md file" -m "Added how to fetch data from website into .md file. 
# # Html was made legiable and stored in .txt file to be parsed later"
