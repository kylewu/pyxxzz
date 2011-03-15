#!/usr/bin/env python

'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             xxzh.py
    Create Date:      Sun Mar 13 20:39:10 2011

'''


import cookielib, urllib2, urllib, sys, time, re

from BeautifulSoup import BeautifulSoup
import httplib2
#import simplejson

loginURL = 'http://www.renren.com/PLogin.do'
origURL = 'http://www.renren.com/home'
username = 'wenbin15@wenbinwu.com'
password = 'CBAnbaWW'
domain = 'renren.com'

lwURL = 'http://apps.renren.com/littlewar?origin=93'
scenerecommendURL = 'http://xnapi.lw.fminutes.com/api.php?inuId=%s&method=Scene.recommend'
sceneinitURL = 'http://xnapi.lw.fminutes.com/api.php?inuId=%s&method=Scene.init'
friendrunURL = 'http://xnapi.lw.fminutes.com/api.php?inuId=%s&method=Friend.run'
scenerunURL = 'http://xnapi.lw.fminutes.com/api.php?inuId=%s&method=Scene.run'

lw_re = re.compile(".*\"iframe_canvas\".* src=\"(?P<link>[^ ]*)\" .*")
inu_re = re.compile(".*\"inuId=(?P<inuid>[0-9a-z_]*).*")

# NOTE Little War uses link like http://xnapi.lw.fminutes.com/?xxx=xxx
#      GET request is informal when using urllib2   : GET ?xxx=xxx, it should be GET /?xxx=xxx
#      so I use httplib2

class LittleWar():


    def __init__(self):
        self.opener = None

    def post(self,url, parm):
        resp, content = httplib2.Http().request(url, 'POST', body=urllib.urlencode(parm))
        return content

    def get(self, url):
        resp, content = httplib2.Http().request(url)
        return content

    def login(self):

        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        #opener.add_handler(urllib2.HTTPRedirectHandler())

        headers = [(
            'User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) \
            Chrome/8.0.552.237 Safari/534.10')]
        self.opener.addheaders = headers

        post_parm = ({
            'email' : username,
            'password' : password,
            'origURL' : origURL,
            'domain' : domain
                    })

        req = urllib2.Request(loginURL, urllib.urlencode(post_parm) )
        
        res = self.opener.open(req)

        if res.geturl() == 'http://www.renren.com/home' :
            return True
        return False

    def init(self):
        # go to littlewar
        res = self.opener.open(lwURL).read()
        soup = BeautifulSoup(res)
        next_link = soup.iframe['src']
        print next_link

        # open little war frame and get inuid
        res = self.get(next_link)

        inuid = 0

        soup = BeautifulSoup(res)
        tags = soup.findAll('param')
        for t in tags:
            m = inu_re.match(t.__str__())
            if m:
                inuid = m.group('inuid')
                break

        print inuid
        return inuid

    def fetch_data(self, inuid):
        scene_recommend = self.get(scenerecommendURL % inuid)

        # scene init
        userinfo = self.post(sceneinitURL % inuid, {'data':'null'})
        print userinfo

        # get keyname and data from userinfo
        keyname = ''
        data = ''

        # friend run
        friend_run = self.post(friendrunURL % inuid, {'keyName':keyname, 'data':data, 'requestSig':''})

        # update data
        data = ''

        # scene run
        scene_run = self.post(scenerecommendURL % inuid, {'keyName':keyname, 'data':data, 'requestSig':''})






    def start(self):
    
        if not lw.login() :
            sys.exit()

        print 'Login success!'
        inuid = self.init()
        self.fetch_data(inuid)

def getIncByName(keyName):
        map = {}

        map["97ba558178f22af9"] = 1;  
        map["8a57faa3ff0c2cd0"] = 2;  
        map["b05395426617a666"] = 3;  
        map["8054b38ece415448"] = 4;  
        map["5a0815d2500be4c3"] = 5;  
        map["cb47e040c444bb13"] = 6;  
        map["4f0b466d4e838204"] = 7;  
        map["9bb033dd03a03a21"] = 8;  
        map["a548d6aefbeb32e0"] = 9;  
        map["c156d1c03531d5f6"] = 10;  

        return map[keyName];  
def md5(str):
    res = ''
    for i in range(len(str)):
        print str[i]
        t = int(0xFF and str[i])

        if( len(hex(t)) == 3):
            res += '0' + hex(t)
        else:
            res += hex(t)

    print res
    return res
         
        #for (int i = 0; i < byteArray.length; i++) {                
            #if (Integer.toHexString(0xFF & byteArray[i]).length() == 1)    
                #md5StrBuff.append("0").append(Integer.toHexString(0xFF & byteArray[i]));    
            #else    
                #md5StrBuff.append(Integer.toHexString(0xFF & byteArray[i]));    
        #}    
         
        #return md5StrBuff.toString();  
    
def getSig(key, keyName):
    inc = getIncByName(keyName);  
      

    print l2
    l2 = l2[1:7]
    l2 = l2[:6]
    print l2
    print int(l2, 16)
    
      
      
    #String a = p1.substring(0, 6);  
    #int v = Integer.parseInt(a, 16);  
    #v = v + inc;  
    #System.out.println(v);  
    #a = Md5(v+"");  
    #return a;  

if __name__ == '__main__':
    lw = LittleWar()
    #lw.start()
        
    
    f = open('sceneinit')
    str = f.read(99999999)

    key = unicode('6eceeac2c76a2b2c0e2018a101f2b76e')
    keyName = unicode("5a0815d2500be4c3")
    sig='49eddcbf48b40de32e809afdc5f8b450'
    #getSig(key, keyName)
    md5(key)

