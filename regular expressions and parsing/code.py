import re
import csv
import sys

dic_URL={}

def readFile():
    """
    This function retrieves URL from file "top500Domains.csv"
    """
    all_URLs=[]
    with open('top500Domains.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                all_URLs.append(row[1])
    #for testing, uncomment this section:
    # all_URLs=["file://localhost:4040/zip_file", "reverbnation.com"]
   

    return all_URLs

def identify_i(URL):
    """
    This function parses the URL (for example: https://www.apple.com/shop/buy-mac/last_page?q=search) and stores, if any:
        *) the parameters, which any value in the URL after a "?". In the example: q=search
    This function also  evaluates if there is a protocol, which is any value before after "://".If the value does not follow a "://", it adds a comment that the value could not be parsed. If there is a protocol, it assigned i=1, otherwise i=0. In the example: https, so i=1   
    """
    global dic_URL
    #remove parameters 
    dic_URL.update({'Original URL':URL})
    URL=URL.split("?")

    if len(URL)>=2:
        parameters= URL[1]
    else:
        parameters= []

    URL=URL[0] 
    dic_URL.update({'Parameters':parameters}) 

    regex=re.compile(r"(?P<protocol>(:\/\/))")
    if regex.match(URL) != "":
        i = 0
        dic_URL.update({'Comments':i})
        return i, URL
        
    else:
        regex=re.compile(r"(?P<protocol>(^[^://]*$))")
        if regex.match(URL) != "":
            i = 1
            dic_URL.update({'Comments':i})
            return i, URL
        else:
            dic_URL.update({'Comments':'the URL submitted does not belong to any of the cases built in this program'})
            return URL

def case0(URL):
    """
    This function parses URL with a structure similar to the following examples:
    https://www.reverbnation.com | https://www.apple.com/shop/buy-mac/pro_13_inc?q=search | file://localhost:4040/zip_file
    This function extracts the following information from the URL:
        *) the protocol, which is any value before after "://". In the second example: https
        *) the domain, which is the first value after the protocol was removed. In the second example: www.apple.com
        *) the last page, which is the last value after the protocol was removed. In the second example: pro_13_inc
        *) the first page, which is the first value after the domain. In the second example: buy_mac
    """
    global dic_URL
    try:
        URL=URL.split('://')
        protocol= URL[0]
        URL=URL[1]
    except:
        protocol= ""

    try:
        URL=URL.split('/')
        domain= URL[0]
        lastPage= URL[-1]
        firstPage= URL[1]
    except:     
        domain= ""
        lastPage= "/"
        firstPage= "/"

    dic_URL.update({'Protocol':protocol,'Domain':domain,'Last Page':lastPage, "First Page": firstPage})
    print(dic_URL)
    return URL

def case1(URL):
    """
    This function parses URL with a structure similar to the following examples:
    reverbnation.com
    This function extracts the following information from the URL:
    *) the protocol, which is any value before after "://". In the second example: https
    *) the domain, which is the first value after the protocol was removed. In the second example: www.apple.com
    *) the last page, which is the last value after the protocol was removed. In the second example: pro_13_inc
    *) the first page, which is the first value after the domain. In the second example: buy_mac
    """
    global dic_URL

    protocol=""
    
    try:
        URL=URL.split('/')
        domain= URL[0]
        lastPage= URL[-1]
        firstPage= URL[1]
    except:     
        domain= ""
        lastPage= ""
        firstPage= ""

    dic_URL.update({'Protocol':protocol,'Domain':domain,'Last Page':lastPage, "First Page": firstPage})
    return URL
    
def save_in_doc():
    """
    This function writes a dictionary to CSV file named "output.csv"
    """
    global dic_URL

    dic={}
    dic=dic_URL
    cvs_columns=dic.keys()
    f = "output.csv"

    try:
        csv_file = open(f, 'w')
    except OSError:
        print ("Could not open/read file:", f)
        sys.exit(0)

    with open(f, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=cvs_columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerow(dic_URL)
        csv_file.close()
  
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

if __name__ == '__main__':
  main()