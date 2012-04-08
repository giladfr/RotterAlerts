#!/usr/bin/python
from BeautifulSoup import BeautifulSoup,NavigableString
import re
import urllib2
import codecs
import pickle
import os
import prowl
import sys
import urllib
#import gmail


class RotterUPS(object):
    def __init__(self):
        self.keyword_file = "rotter_keywords.lst"
        self.cache_file = "rotter_cache.db"
        self.rotter_address = "http://rotter.net/cgi-bin/listforumiphone.pl"
        self.scoop_text_list = []
        self.scoop_time_list = []
        self.db = []
        self.key_words = []
        self.debug = False
        self.xbmc = False


    def add_keywords(self):
        kf = open(self.keyword_file,"a")
        print "Enter keyword, 'x' to finish"
        inp = ""
        while True:
            inp = unicode(raw_input(),"utf8")
            if inp == "x":
                break
            kf.write(repr(inp))
            kf.write("\n\r")
            kf.flush()
        kf.close()




    def load_db(self):
        if os.path.exists(self.cache_file):
            f = open(self.cache_file,"r")
            self.db = pickle.load(f)
            f.close()
        kf = open(self.keyword_file,"r")
        for line in kf.readlines():
            if line != " ":
                try:
                    self.key_words.append(eval(line))
                except:
                    pass
        kf.close()

    def load_soup(self):
        #page = urllib2.urlopen(self.rotter_address)
        #headers = { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }
        headers = { 'User-Agent' : 'Mobile Safari 1.1.3 (iPhone; U; CPU like Mac OS X; en)' }
        req = urllib2.Request(self.rotter_address, '', headers)
        response = urllib2.urlopen(req).read()
        self.soup = BeautifulSoup(response)
        raw_scoop_list = self.soup.findAll("td",align="right")
        raw_time_list = self.soup.findAll("td",align="center")
        for scoop_num in range(len(raw_time_list)-1):
            scoop = {}
            scoop["text"] = eval(raw_scoop_list[scoop_num].find("b").contents[0].string.__repr__())
            scoop["time"] = eval(raw_time_list[scoop_num].find("b").contents[0].string.__repr__())
            scoop["url"] = raw_scoop_list[scoop_num].find("a")["href"]
            if (scoop["text"] != None) and not(self.exist_in_db(scoop)):
                self.db.append(scoop)
                if self.match_key_words(scoop):
                    scoop["fcontents"] = self.get_fcontents(scoop)
                    self.send_prowl(scoop)
                    if self.xbmc == True:
                        self.send_xbmc(scoop)

    def match_key_words(self,scoop):
        for key_word in self.key_words:
            #print scoop["text"]
            if scoop["text"].find(key_word) > -1:
                return True
        return False


    def exist_in_db(self,scoop):
        for db_scoop in self.db:
            if scoop["text"] == db_scoop["text"]:
                return True
        return False

    def print_db(self):
        for db_scoop in self.db:
            print db_scoop["text"]

    def send_prowl(self,scoop):
        if self.debug:
            print "Debug Prowl | Time: %s | MSG: %s" %(scoop["time"], scoop["text"])
        else:
            prowl.send("Rotter Alert",scoop["text"],scoop["fcontents"],-1,scoop["url"])

    def send_xbmc(self,scoop):
       print scoop["text"]
       os.system("wget http://192.168.1.103:8080/xbmcCmds/xbmcHttp?command=ExecBuiltIn(Notification(RotterAlert," + scoop['text'] + ",30000))")

        

    def save_db(self):
        f = codecs.open(self.cache_file, 'w')
        self.db = pickle.dump(self.db,f)
        f.close()

    def get_fcontents(self,scoop):
        #print "Getting fcontents of ",scoop["text"]
        headers = { 'User-Agent' : 'Mobile Safari 1.1.3 (iPhone; U; CPU like Mac OS X; en)' }
        req = urllib2.Request(scoop["url"] ,'', headers)
        response = urllib2.urlopen(req).read()
        contents_soup = BeautifulSoup(response)
        tables = contents_soup.findAll("table")
        contents =  u"".join([s.string for s in tables[14].findAll(text=True)]).replace("&nbsp;","").replace("\n"," ")
        return contents









if __name__ == "__main__":
    rotter = RotterUPS()
    if len(sys.argv) > 1:
        if sys.argv[1]=="keywords":
            rotter.load_db()
            for keyword in rotter.key_words:
                print keyword
            rotter.add_keywords()

        if sys.argv[1] == 'debug':
            rotter.debug = True
            rotter.load_db()
            rotter.load_soup()
            rotter.save_db()

        if sys.argv[1] == 'cache':
            rotter.load_db()
            rotter.print_db()
        
        if sys.argv[1] == 'xbmc':
            rotter.xbmc = True
            rotter.load_db()
            rotter.load_soup()
            rotter.save_db()
            


    else:
        rotter.load_db()
        rotter.load_soup()
        rotter.save_db()
