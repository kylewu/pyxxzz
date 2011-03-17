#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""*
 * ----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <admin@wenbinwu.com> wrote this file. As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a beer in return Wenbin Wu
 * ----------------------------------------------------------------------------
 *"""

'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             xxzh.py
    Create Date:      Sun Mar 13 20:39:10 2011

'''


import cookielib, urllib2, urllib
import sys, time, re
import hashlib

from BeautifulSoup import BeautifulSoup
import httplib2
import simplejson as json

username = 'wenbin11@wenbinwu.com'
password = 'password'

# 24 Hours
produce_id = 4

loginURL = 'http://www.renren.com/PLogin.do'
origURL  = 'http://www.renren.com/home'
domain   = 'renren.com'

# RE
lw_re  = re.compile(".*\"iframe_canvas\".* src=\"(?P<link>[^ ]*)\" .*")
inu_re = re.compile(".*\"inuId=(?P<inuid>[0-9a-z_]*).*")

lwURL = 'http://apps.renren.com/littlewar?origin=93'

# Base URL
fminutesURL = 'http://xnapi.lw.fminutes.com/'

# GET
scenerecommendURL = fminutesURL + 'api.php?inuId=%s&method=Scene.recommend'
scene_init_URL    = fminutesURL + 'api.php?inuId=%s&method=Scene.init'

friend_run_URL    = fminutesURL + 'api.php?inuId=%s&method=Friend.run'
scene_run_URL     = fminutesURL + 'api.php?inuId=%s&method=Scene.run'

friend_run_data   = '{"friendlistVer":"%d"}'
scene_run_data    = '{"fid":"%d"}'

# POST
gain_food_URL       = fminutesURL + 'api.php?inuId=%s&method=Produce.gainFood'
produce_food_URL    = fminutesURL + 'api.php?inuId=%s&method=Produce.produceFood'
gain_soldier_URL    = fminutesURL + 'api.php?inuId=%s&method=Produce.gainRecruitment'
produce_soldier_URL = fminutesURL + 'api.php?inuId=%s&method=Produce.recruiteSoldier'
attack_beast_URL    = fminutesURL + 'api.php?inuId=%s&method=Pve.attackBeast'
use_skill_URL       = fminutesURL + 'api.php?inuId=%s&method=Skill.useSkill'
defence_loot_URL    = fminutesURL + 'api.php?inuId=%s&method=Defence.loot'            # Chen Huo Da Jie
accept_reward_URL   = fminutesURL + 'api.php?inuId=%s&method=Reward.acceptReward'     # Dong Ta Yi Xia
# DATA
gain_food_data      = '{"ids":%s,"id":%d}'
produce_food_data   = '{"produce_id":%d,"id":%d}'
gain_soldier_data   = '{"id":%d}'
produce_soldier_data= '{"produce_id":%d,"id":%d}'
attack_beast_data   = '{"pointId":%d,"fId":"%d"}'
use_skill_data      = '{"skillId":%d,"fId":"%d"}'
defence_loot_data   = '{"desc_id":"%d"}'
accept_reward_data  = '{"actId":%d,"fId":"%d"}'

# Not Supported
feed_reward_URL     = fminutesURL + 'api.php?inuId=%s&method=Reward.acceptFeedReward' 
feed_reward_data    = '{"actId":%d,"fId":"%d"}'
defence_fight_URL   = fminutesURL + 'api.php?inuId=%s&method=Defence.fight'
defence_fight_data  = '{"ids":%s,"troops":{%d":%d},"desc_id":"%d"}'
defence_riot_URL    = fminutesURL + 'api.php?inuId=%s&method=Defence.riot'            # Pai Bing Zhan Ling
defence_riot_data   = '{"ids":%s}'
defence_help_URL    = fminutesURL + 'api.php?inuId=%s&method=Defence.help'            # Pai Bing Ying Jiu
defence_help_data   = '{"ids":%s,"troops":{"90002":178},"desc_id":"%d"}'

# NOTE 1. Little War uses link like http://xnapi.lw.fminutes.com/?xxx=xxx
#      GET request is informal when using urllib2   : GET ?xxx=xxx, it should be GET /?xxx=xxx
#      so I use httplib2
#      2. httplib2 user-agent contains # sign which may cause problem

class User():
      
    def __init__(self):
        self.id               = 0
        self.food             = 0
        self.grade            = 0
        self.mp               = 0
        self.population       = 0
        self.population_limit = 0
        self.population_all   = 0

        self.time = 0

    def setTime(self, time):
        self.time = time

    def update(self, user):                                                                                                                         
        self.id               = user["uid"]
        self.food             = user["food"]
        self.population       = user["population"]
        self.population_all   = user["population_all"]
        self.population_limit = user["population_limit"]
        self.grade            = user["grade"]
        self.mp               = user["mp"]

    def log(self):
        print 'id %d grade %d food %d population %d population_all %d population_limit %d mp %d' % (self.id, self.grade,
                                                                                                    self.food,
                                                                                                    self.population,
                                                                                                    self.population_all,
                                                                                                    self.population_limit,
                                                                                                    self.mp)
    
class LittleWar():

    def __init__(self):
        self.opener = None
        self.headers = {'Content-type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel\
                   Mac OS X 10_6_4; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133'}

    def post(self,url, parm):
        resp, content = httplib2.Http().request(url, 'POST', headers=self.headers, body=urllib.urlencode(parm))
        return content

    def get(self, url):
        resp, content = httplib2.Http().request(url, headers=self.headers)
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
        #print next_link

        # open little war frame and get inuid
        res = self.get(next_link)

        soup = BeautifulSoup(res)
        tags = soup.findAll('param')
        for t in tags:
            m = inu_re.match(t.__str__())
            if m:
                self.inuid = m.group('inuid')
                break
        #print 'inuID %s' % self.inuid

    def fetch_data(self):
        # scene recommend
        #scene_recommend = self.get(scenerecommendURL % self.inuid)

        # scene init
        userinfo = self.post(scene_init_URL % self.inuid, {'data':'null'})
        #print userinfo

        # get keyname and data from userinfo
        userinfo = json.loads(userinfo)

        self.keyName = userinfo['info']['getKey']['keyName']
        self.key = userinfo['info']['getKey']['key']

        # compute sig
        self.requestSig = self.get_sig(self.key, self.keyName)
        #print self.keyName, self.key, self.requestSig

        # user info
        self.user = User()
        self.user.update(userinfo['info']['player_info'])
        self.user.setTime(userinfo['info']['time'])
        #self.user.log()

        # friend run
        friendrun = self.post_friend_run(self.user.time)

        # visit myself
        scenerun = self.post_scene_run_without_sig(self.user.id)
        print 'user id %d' % self.user.id

        # 1 : Finish personal job at home
        scenerun = json.loads(scenerun)
        # 1.1 : Try to use skills
        self.use_skill(userinfo)
        # 1.2 : Try to harvest both food and soldier
        # TODO test harverst and then produce
        self.harvest(scenerun)
        # 1.3 : Kill animals at home
        self.attack_beast(scenerun)

        # 2 : check friends
        friendrun = json.loads(friendrun)
        self.visit_friends(friendrun)

    def visit_friends(self, data):
        friends = data['info']['gameData']['data']
        slaves  = data['info']['gameData']['slave']
        print '%d friends' % len(friends)

        # Go to every friends home
        for friend in friends.values():
            self.visit(friend['uid'], friend['uid'] in slaves)

    def visit(self, id, is_slave):
        print 'visiting %d' % id
        data = self.post_scene_run(id)
        data = json.loads(data)
        # attack beast
        self.attack_beast(data)

        if is_slave:
            print 'dong ta yi xia'
            # Dong Ta Yi Xia
            self.post_accept_reward(slave)
            return 

        if data['info']['enter_scene'].has_key('loot_flag'):
            loot_flag = data['info']['enter_scene']['loot_flag']
        else:
            loot_flag = -1

        loot_times = data['info']['enter_scene']['loot_times']
        master_info = data['info']['enter_scene']['master_info']
        if loot_flag == 0 and len(master_info) and loot_times < 15 > 0:
            print 'chen huo da jie'
            # Chen Huo Da Jie
            self.post_defence_loot(id)

        return

    def attack_beast(self, data):
        fId = data['info']['enter_scene']['player_info']['uid']
        pve = data['info']['enter_scene']['pve']
        if pve is None:
            return
        #print fId
        #print pve
        if pve.__class__.__name__ == 'dict':
            for beast in pve.values():
                #print beast['pointId']
                self.post_attack_beast(beast['pointId'], fId)
        else:
            for beast in pve:
                #print beast['pointId']
                self.post_attack_beast(beast['pointId'], fId)

    def use_skill(self, data):
        skillList = data['info']['skillList']

        # YeShouHaoJiao          1
        # TianJiangShenBing      2
        # MiHuanZhiXiang         26
        if self.user.time > skillList['1']['canUseTime']:
            self.post_use_skill(1, self.user.id)
        if self.user.time > skillList['26']['canUseTime']:
            self.post_use_skill(26, self.user.id)

    def harvest(self, data):

        build_list = data['info']['enter_scene']['build_info']['build_list']

        food_ids = []
        food_list = []

        for build in build_list.values():

            build_id = build['build_id']

            if build_id >= 30000 and build_id < 40000:
                #### FOOD ####
                # To gain food, a list of all food id need to be sent
                food_list.append(build)
                food_ids.append(build['id'])
            elif build_id >= 40000 and build_id < 50000:
                #### ARMY ####
                self.harvest_soldier(build)

        for i in range(len(food_ids)):
            self.harvest_food(food_list[i], food_ids)

    def harvest_food(self, food, food_ids):
        # empty
        if food['start_time'] == 0:
            self.post_produce_food(food['id'])
        # finish
        elif food['end_time'] < self.user.time:
            # gain food
            self.post_gain_food(food['id'], food_ids)
            # produce food
            self.post_produce_food(food['id'])

    def harvest_soldier(self, soldier):
        # empty
        if soldier['start_time'] == 0:
            self.post_produce_soldier(soldier['id'])
        # finish
        elif soldier['end_time'] < self.user.time:
            # gain soldier
            self.post_gain_soldier(soldier['id'])
            # produce soldier
            self.post_produce_soldier(soldier['id'])

    def post_accept_award(self, id):
        return self.post(accept_reward_URL % self.inuid,
                         {'keyName':self.keyName, 'data':accept_reward_data % id, 'requestSig':self.requestSig})

    def post_defence_loot(self, id):
        return self.post(defence_loot_URL % self.inuid,
                         {'keyName':self.keyName, 'data':defence_loot_data % id, 'requestSig':self.requestSig})

    def post_friend_run(self, time):
        print 'post friend run'
        return self.post(friend_run_URL % self.inuid,
                         {'keyName':self.keyName, 'data':friend_run_data % time, 'requestSig':''})

    def post_scene_run_without_sig(self, id):
        print 'post scene run'
        return self.post(scene_run_URL % self.inuid, 
                         {'keyName':self.keyName, 'data':scene_run_data % id, 'requestSig':''})

    def post_scene_run(self, id):
        print 'post scene run'
        return self.post(scene_run_URL % self.inuid, 
                         {'keyName':self.keyName, 'data':scene_run_data % id, 'requestSig':self.requestSig})
    
    def post_gain_food(self, id, ids):
        print 'post gain food'
        return self.post(gain_food_URL % self.inuid,
                         {'keyName':self.keyName, 'data':gain_food_data % (ids, id), 'requestSig':self.requestSig})

    def post_produce_food(self, id):
        print 'post produce food'
        return self.post(produce_food_URL % self.inuid,
                         {'keyName':self.keyName, 'data':produce_food_data % (produce_id, id), 'requestSig':self.requestSig})

    def post_gain_soldier(self, id):
        print 'post gain soldier'
        return self.post(gain_soldier_URL % self.inuid,
                         {'keyName':self.keyName, 'data':gain_soldier_data % (id), 'requestSig':self.requestSig})

    def post_produce_soldier(self, id):
        print 'post produce soldier'
        return self.post(produce_soldier_URL % self.inuid, 
                    {'keyName':self.keyName, 'data':produce_soldier_data % (produce_id, id), 'requestSig':self.requestSig})

    def post_use_skill(self, skillId, fId):
        print 'post use skill'
        return self.post(use_skill_URL % self.inuid,
                  {'keyName':self.keyName, 'data':use_skill_data % (skillId, fId), 'requestSig':self.requestSig})

    def post_attack_beast(self, pointId, fId):
        print 'post attack beast'
        return self.post(attack_beast_URL % self.inuid,
                  {'keyName':self.keyName, 'data':attack_beast_data % (pointId, fId), 'requestSig':self.requestSig})

    def get_inc(self, keyName):
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

    def md5(self, key):
        m = hashlib.md5()
        m.update(key.encode('utf-8'))
        r = m.digest()
        return r.encode("hex")

    def get_sig(self, key, keyName):
        inc = self.get_inc(keyName);  

        res = self.md5(key)
        res = self.md5(res)
        res = self.md5(res[1:7])
        res = '%d' % (int(res[:6], 16) + inc)
        res = self.md5(res)

        return res

    def start(self):
        """ Start job """ 
        if not lw.login() :
            sys.exit()

        print 'Login success!'
        self.init()
        self.fetch_data()

def check_sig():
    key = "9eeb28f7617b482ab001f67043b3e177"
    keyName = "a548d6aefbeb32e0"
    requestSig='fc5e065b5c9b3bc528fad54a195533ee'

    lw = LittleWar()
    print lw.get_sig(key, keyName)
    if lw.get_sig(key, keyName) == requestSig:
        print 'ok'

def test_json():
    f = open('a')
    str = f.read(999999)
    j = json.loads(str)
    print 'aaaaaa'
    print ['info']['enter_scene']['player_info']['pve']

def check():
    f1 = open('cc')
    f1 = f1.read(999999)
    f2 = open('dd')
    f2 = f2.read(999999)
    print len(f1), len(f2)
    for i in range(len(f1)):
        if f1[i] != f2[i]:
            print i
            print f1[i:]
            break
            print '1111111111111'

if __name__ == '__main__':
    lw = LittleWar()
    lw.start()
    #test_json()
    #check()
