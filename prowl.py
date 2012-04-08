#!/usr/bin/python
import sys,urllib
API_GILAD = "697854991b6f266a4a0de4a9200abbe9bd641c48"
API_ESHEL = "4e6ad011a9659841e969ed2fe38996cb70d40435"


#API_LIST = [API_GILAD,API_ESHEL]
API_LIST = [API_GILAD]

def send(application,title,description,priority,url = ""):
    description = urllib.quote(description.encode('utf8'))
    title = urllib.quote(title.encode('utf8'))
    for API in API_LIST:
        urllib.urlopen("https://prowl.weks.net/publicapi/add?apikey=" + API + "&priority="+ str(priority) + "&application=" + application +"&event=" + title+ "&description=" + description + "&url=" + url)


if __name__ == "__main__":
    send("app","title",urllib.quote(u"\u05d0".encode('utf8')),0);

