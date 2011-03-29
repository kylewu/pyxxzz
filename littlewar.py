#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''*
 * ----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <admin@wenbinwu.com> wrote this file. As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a beer in return Wenbin Wu
 * ----------------------------------------------------------------------------
 *'''

'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             xxzh.py
    Create Date:      Sun Mar 13 20:39:10 2011

'''

import cookielib, urllib2, urllib
import sys, time, re, os
import hashlib
from datetime import datetime
import time
import threading

from BeautifulSoup import BeautifulSoup
import httplib2
import simplejson as json

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
accept_reward_URL   = fminutesURL + 'api.php?inuId=%s&method=Reward.acceptFeedReward' # Dong Ta Yi Xia
daily_reward_URL    = fminutesURL + 'api.php?inuId=%s&method=Reward.acceptReward'    

# DATA
gain_food_data      = '{"ids":%s,"id":%d}'
produce_food_data   = '{"produce_id":%d,"id":%d}'
gain_soldier_data   = '{"id":%d}'
produce_soldier_data= '{"produce_id":%d,"id":%d}'
attack_beast_data   = '{"pointId":%d,"fId":"%d"}'
use_skill_data      = '{"skillId":%d,"fId":"%d"}'
defence_loot_data   = '{"desc_id":"%d"}'
accept_reward_data  = '{"actId":%d,"fId":"%d"}'

# Special 
#send_spy_URL        = fminutesURL + 'api.php?inuId=%s&method=spy.sentSpy'
#send_spy_data       = '{"placeId":%d,"fId":"%d"}'
#recv_treasure_URL   = fminutesURL + 'api.php?inuId=%s&method=spy.recieveTreasure'
#recv_treasure_data  = '{"placeId":%d}'

# Not Supported
defence_riot_URL    = fminutesURL + 'api.php?inuId=%s&method=Defence.riot'            # Fan Kang
defence_riot_data   = '{"ids":%s}'
defence_fight_URL   = fminutesURL + 'api.php?inuId=%s&method=Defence.fight'           # Pai Bing Zhan Ling
defence_fight_data  = '{"ids":%s,"troops":{%d":%d},"desc_id":"%d"}'
defence_help_URL    = fminutesURL + 'api.php?inuId=%s&method=Defence.help'            # Pai Bing Ying Jiu
defence_help_data   = '{"ids":%s,"troops":{"90002":178},"desc_id":"%d"}'

beast_type = {  
                2001 : ('Ju Xi'         , 5 )  ,
                2002 : ('Ban Chi Xi'    , 10)  ,
                2004 : ('Ba Wang Long'  , 40)  ,
                2005 : ('Ye Zhu'        , 5 )  ,
                2006 : ('Zong Xiong'    , 10)  ,
                2007 : ('Meng Ma Xiang' , 20)  ,

                2020 : ('Lv Kong Que'   , 12)  ,
                2023 : ('Da Mi Tan'     , 100) ,
             }

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

        self.friend_list = list()
        self.slave_list = list()
        self.touched_list = list()

        self.troops = dict()

        self.time = 0


    def setTime(self, time):
        self.time = time

    def update_touched_list(self, tl):
        self.touched_list = []
        if not len(tl) == 0:
            for t in tl.keys():
                self.touched_list.append(int(t))

    def update_friend_list(self, friends):
        self.friend_list = []
        for friend in friends.values():
            self.friend_list.append(friend['uid'])
        self.friend_list.remove(1)

    def update_slave_list(self, slaves):
        self.slave_list = slaves

    def update(self, user):                                                                                                                         
        self.id               = user["uid"]
        self.food             = user["food"]
        self.population       = user["population"]
        self.population_all   = user["population_all"]
        self.population_limit = user["population_limit"]
        self.grade            = user["grade"]
        self.mp               = user["mp"]

        for army in user["troops"].values():
            for id in army:
                self.troops[id] = army[id]


    def log(self):
        print 'id %d grade %d food %d population %d population_all %d population_limit %d mp %d' % (self.id, self.grade,
                                                                                                    self.food,
                                                                                                    self.population,
                                                                                                    self.population_all,
                                                                                                    self.population_limit,
                                                                                                    self.mp)
        print 'friend list : %s' % self.friend_list
        print 'slave list : %s' % self.slave_list
    

class LittleWar():

    def __init__(self, username, password, produce_id=1, logfile='log'):

        try: 
            self.logfile = open (logfile, "a")
        except:
            print "Error opening log file"
            raise

        self.username = username
        self.password = password
        self.opener   = None
        self.headers  = {'Content-type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel\
                   Mac OS X 10_6_4; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133'}

        self.produce_id = produce_id

    def log(self, msg):
        self.logfile.write('%s : %s\n' % (self.username, msg))
        self.logfile.flush()

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
            'email'    : self.username,
            'password' : self.password,
            'origURL'  : origURL,
            'domain'   : domain
                    })

        req = urllib2.Request(loginURL, urllib.urlencode(post_parm) )
        
        res = self.opener.open(req)

        if res.geturl() == 'http://www.renren.com/home' :
            return True
        print res.geturl()
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

    def work(self):
        # scene recommend
        #scene_recommend = self.get(scenerecommendURL % self.inuid)

        # scene init
        userinfo = self.post(scene_init_URL % self.inuid, {'data':'null'})
        #print userinfo

        # get keyname and data from userinfo
        userinfo = json.loads(userinfo)

        # user info
        self.user = User()
        self.user.update(userinfo['info']['player_info'])
        self.user.setTime(userinfo['info']['time'])
        self.user.update_touched_list(userinfo['info']['actionList'])

        self.keyName = userinfo['info']['getKey']['keyName']
        self.key = userinfo['info']['getKey']['key']

        # compute sig
        self.requestSig = self.get_sig(self.key, self.keyName)
        #print self.keyName, self.key, self.requestSig

        # friend run
        friendrun = self.post_friend_run(self.user.time)
        
        # friend list and slave list
        friendrun = json.loads(friendrun)
        self.user.update_friend_list(friendrun['info']['gameData']['data'])
        self.user.update_slave_list(friendrun['info']['gameData']['slave'])
        #self.user.log()

        # visit myself
        self.log('my id %d' % self.user.id)
        scenerun = self.post_scene_run_without_sig(self.user.id)

        # 0 : Daily reward
        if userinfo['info']['rewardItems'] is not None:
            self.log('daily reward')
            self.post_daily_reward()

        # 1 : Finish personal job at home
        scenerun = json.loads(scenerun)

        # 1.1 : Try to use skills
        self.log('check skill')
        self.use_skill(userinfo)
        # 1.2 : Try to harvest both food and soldier
        self.log('check food and soldier')
        self.harvest(scenerun)

        # 1.3 : Kill animals at home
        self.log('check animal')
        self.attack_beasts(scenerun)

        a = time.time()
        # 2 : check friends
        self.visit_friends()
        b = time.time()

        # 3 : Special 

        # Spy case
        #if self.user.id == 59094425:
            #b = time.time()
            #return int(b-a)
        #scenerun = self.post_scene_run(self.user.id)
        #scenerun = json.loads(scenerun)
        #self.spy_case(scenerun)

        return int(b-a)

    # Special spy case started in Mar 17 2011
    #def spy_case(self, data):
        #self.log('check spy')
        #ids = [59094425,355852754,356032671,356151199,356298870,356527009,356837352]
        #ids.remove(self.user.id)
        #if self.user.id == 59094425:
            #ids.append(229266798)
            #ids.append(277307056)
            #ids.append(84744)
            #ids.append(222799676)

        #if not data['info']['enter_scene'].has_key('spy'):
            #return

        #spy = data['info']['enter_scene']['spy']

        #for i in range(len(spy)):

            #s = spy[i]
            #if s['status'] == 0:
                #continue

            #self.log('try to send spy %d' % i)
            #b = False
            #for id in ids:
                #b = self.deal_spy_case(i, id)
                #if b:
                    #break
            #if not b:
                #self.log('try to send to friend')
                #purl_friends = [f for f in self.user.friend_list if not f in ids]
                ## send to friends
                #for id in purl_friends:
                    #if self.deal_spy_case(i, id):
                        #break

    #def deal_spy_case(self, placeId, id):
        #if self.user.population < 100:
            #return False

        #res = self.post_send_spy(placeId, id)
        #res = json.loads(res)

        #if res['info'].has_key('player_info'): # success in sending a spy
            #self.user.update(res['info']['player_info'])
            #self.log('success in sending spy to %d' % id)
            #self.post_recv_treasure(placeId)
            #return True
        #return False


    def visit_friends(self):
        self.log('Total %d friends' % len(self.user.friend_list))

        # Go to every friends home
        for friend in self.user.friend_list:
            self.visit(friend, friend in self.user.slave_list)

    def visit(self, id, is_slave):
        self.log ('Visiting %d' % id)
        data = self.post_scene_run(id)
        data = json.loads(data)

        # attack beast
        self.attack_beasts(data)

        if is_slave and (not id in self.user.touched_list) and len(self.user.touched_list) < 4:
            self.log('dong ta yi xia')
            # Dong Ta Yi Xia
            self.post_accept_reward(23, id)
            return 

        if data['info']['enter_scene'].has_key('loot_flag'):
            loot_flag = data['info']['enter_scene']['loot_flag']
        else:
            loot_flag = -1

        loot_times = data['info']['enter_scene']['loot_times']
        master_info = data['info']['enter_scene']['master_info']
        if loot_flag == 0 and len(master_info) and loot_times < 15 > 0:
            self.log('chen huo da jie')
            # Chen Huo Da Jie
            self.post_defence_loot(id)

        return

    def attack_beasts(self, data):
        fId = data['info']['enter_scene']['player_info']['uid']
        pve = data['info']['enter_scene']['pve']
        if pve is None:
            return
        #print fId
        #print pve
        if pve.__class__.__name__ == 'dict':
            for beast in pve.values():
                if not self.attack_beast(beast, fId):
                    break
        else:
            for beast in pve:
                if not self.attack_beast(beast, fId):
                    break

    def attack_beast(self, beast, fId):
        # check if the beast is in our map
        if beast_type.has_key(beast['beastId']):
            name, force = beast_type[beast['beastId']]
        else:
            old_popu = self.user.population
            name = 'unknow animal'
            force = 200

        # compute how many soldiers are needed
        force = beast['beastNum'] * force
        if self.user.population > force:
            res = self.post_attack_beast(beast['pointId'], fId)
            res = json.loads(res)
            self.user.update(res['info']['player_info'])

            # unkown animal, write it down
            if force == 200:
                beast_cap = (old_popu - self.user.population)/beast['beastNum']
                self.log('ID %d : %d' % (beast['beastId'], beast_cap))
                beast_type[beast['beastId']] = ('unknow animal', beast_cap)

            self.log('attack %s' % name)
            return True
        else:
            self.log('no enough population, skip this animal')
            return False

    def use_skill(self, data):
        skillList = data['info']['skillList']

        # YeShouHaoJiao          1
        # TianJiangShenBing      2
        # MiHuanZhiXiang         26
        if self.user.time > skillList['1']['canUseTime']:
            self.post_use_skill(1, self.user.id)
            self.log('YeShouHaoJiao')
        if self.user.time > skillList['26']['canUseTime']:
            self.post_use_skill(26, self.user.id)
            self.log('MiHuanZhiXiang')

    def harvest(self, data):

        build_list = data['info']['enter_scene']['build_info']['build_list']

        food_ids = []
        food_list = []
        soldier_list = []

        for build in build_list.values():

            build_id = build['build_id']

            if build_id >= 30000 and build_id < 40000:
                #### FOOD ####
                # To gain food, a list of all food id need to be sent
                food_list.append(build)
                food_ids.append(build['id'])
            elif build_id >= 40000 and build_id < 50000:
                #### ARMY ####
                soldier_list.append(build)

        for food_build in food_list:
            self.harvest_food(food_build, food_ids)

        for soldier_bulild in soldier_list:
            self.harvest_soldier(soldier_bulild)

    def harvest_food(self, food, food_ids):
        # empty
        if food['start_time'] == 0:
            self.log('produce food')
            self.post_produce_food(food['id'])
        # finish
        elif food['end_time'] < self.user.time:
            # gain food
            self.log('gain food')
            self.post_gain_food(food['id'], food_ids)
            # produce food
            self.log('produce food')
            self.post_produce_food(food['id'])

    def harvest_soldier(self, soldier):
        # empty
        if soldier['start_time'] == 0:
            self.log('try to produce soldier')
            self.post_produce_soldier(soldier['id'])
        # finish
        elif soldier['end_time'] < self.user.time:
            # gain soldier
            self.log('gain soldier')
            self.post_gain_soldier(soldier['id'])
            # produce soldier
            self.log('try to produce soldier')
            self.post_produce_soldier(soldier['id'])

    def post_recv_treasure(self, id):
        return self.post(recv_treasure_URL % self.inuid,
                         {'keyName':self.keyName, 'data':recv_treasure_data % id, 'requestSig':self.requestSig})

    def post_send_spy(self, id, fId):
        return self.post(send_spy_URL % self.inuid,
                         {'keyName':self.keyName, 'data':send_spy_data % (id, fId), 'requestSig':self.requestSig})

    def post_daily_reward(self):
        return self.post(daily_reward_URL % self.inuid,
                         {'keyName':self.keyName, 'data':'null', 'requestSig':self.requestSig})

    def post_accept_reward(self, actId, fId):
        return self.post(accept_reward_URL % self.inuid,
                         {'keyName':self.keyName, 'data':accept_reward_data % (actId, fId), 'requestSig':self.requestSig})

    def post_defence_loot(self, id):
        return self.post(defence_loot_URL % self.inuid,
                         {'keyName':self.keyName, 'data':defence_loot_data % id, 'requestSig':self.requestSig})

    def post_friend_run(self, time):
        #print 'post friend run'
        return self.post(friend_run_URL % self.inuid,
                         {'keyName':self.keyName, 'data':friend_run_data % time, 'requestSig':''})

    def post_scene_run_without_sig(self, id):
        #print 'post scene run'
        return self.post(scene_run_URL % self.inuid, 
                         {'keyName':self.keyName, 'data':scene_run_data % id, 'requestSig':''})

    def post_scene_run(self, id):
        #print 'post scene run'
        return self.post(scene_run_URL % self.inuid, 
                         {'keyName':self.keyName, 'data':scene_run_data % id, 'requestSig':self.requestSig})
    
    def post_gain_food(self, id, ids):
        #print 'post gain food'
        return self.post(gain_food_URL % self.inuid,
                         {'keyName':self.keyName, 'data':gain_food_data % (ids, id), 'requestSig':self.requestSig})

    def post_produce_food(self, id):
        #print 'post produce food'
        return self.post(produce_food_URL % self.inuid,
                         {'keyName':self.keyName, 'data':produce_food_data % (self.produce_id, id), 'requestSig':self.requestSig})

    def post_gain_soldier(self, id):
        #print 'post gain soldier'
        return self.post(gain_soldier_URL % self.inuid,
                         {'keyName':self.keyName, 'data':gain_soldier_data % (id), 'requestSig':self.requestSig})

    def post_produce_soldier(self, id):
        #print 'post produce soldier'
        return self.post(produce_soldier_URL % self.inuid, 
                    {'keyName':self.keyName, 'data':produce_soldier_data % (self.produce_id, id), 'requestSig':self.requestSig})

    def post_use_skill(self, skillId, fId):
        #print 'post use skill'
        return self.post(use_skill_URL % self.inuid,
                  {'keyName':self.keyName, 'data':use_skill_data % (skillId, fId), 'requestSig':self.requestSig})

    def post_attack_beast(self, pointId, fId):
        #print 'post attack beast'
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
        
        t = 0
        self.log('%s : Start working' % datetime.now().strftime("%I:%M%p %B %d %Y"))
        try:
            """ Start job """ 
            if not self.login() :
                self.log('error')
                return

            self.log('Login success!')
            self.init()
            t = self.work()
        except:
            self.log('%s : Error ' % datetime.now().strftime("%I:%M%p %B %d %Y"))
        self.log('%s : Job done' % datetime.now().strftime("%I:%M%p %B %d %Y"))

        self.log('Next job will begin in %d s' % (7200-t))
        return t


def single_start(user, password, produce_id = 1, logfile='log', loop = False):
    if not produce_id in range(1,5):
        print 'produce id can be only from 1 to 4'
        return 

    while True:
        lw = LittleWar(user, password, produce_id, logfile)
        t = lw.start()
        if not loop:
            break
        time.sleep(2*60*60 - t + 5)

def multiple_start(user_list, password, produce_id = 1, logfile='log', loop = False):
    if not produce_id in range(1,5):
        print 'produce id can be only from 1 to 4'
        return

    for user in user_list:
        t = threading.Thread(target=single_start, args=(user, password, produce_id, logfile, loop))
        t.start()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage : python xxzh.py username password [produce_id] [logfile]'
        sys.exit(0)

    if len(sys.argv) == 5:
        single_start(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4])
    elif len(sys.argv) == 4:
        single_start(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    elif len(sys.argv) == 3:
        single_start(sys.argv[1], sys.argv[2])
