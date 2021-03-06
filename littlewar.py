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
import hashlib
import re
import time
import sys
import threading
import logging

from BeautifulSoup import BeautifulSoup
import httplib2
import simplejson as json

main_id = 59094425
last_id = 356837352

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

# Test
# NOT AVAILABLE
defence_riot_URL    = fminutesURL + 'api.php?inuId=%s&method=Defence.riot'            # Fan Kang
defence_riot_data   = '{"round":1,"troops":%s}'

# NOT AVAILABLE
defence_help_URL    = fminutesURL + 'api.php?inuId=%s&method=Defence.help'            # Pai Bing Ying Jiu
defence_help_data   = '{"desc_id":"356837352","ids":[16,17,19,20,21,126,8,9,35,14,15],"troops":{"90005":0,"90007":79},"round":1}'

defence_fight_URL   = fminutesURL + 'api.php?inuId=%s&method=Defence.fight'           # Zhan Ling
first_defence_fight_data  = '{"round":1,"desc_id":"%d","troops":%s,"ids":[16,17,19,20,21,126,8,9,35,14,15]}'
defence_fight_data  = '{"desc_id":"%d","ids":[16,17,19,20,21,126,8,9,35,14,15]}'


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

        self.troops = dict()
        if len(user["troops"]) == 0:
            return

        army = user['troops']['%d'%self.id]
        for id in army:
            self.troops[id] = army[id]['num']

    def troops_str(self):
        tl = list()
        for t in self.troops.keys():
            tl.append('"%s":%d' % (t, self.troops[t]))

        return '{%s}' % ','.join(tl)

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

    def __init__(self, username, password, produce_id, logger):

        self.username = username
        self.password = password
        self.opener   = None
        self.headers  = {'Content-type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel\
                   Mac OS X 10_6_4; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133'}

        self.produce_id = produce_id

        self.logger = logger

    def post(self, url, parm):
        resp, content = httplib2.Http(timeout=15).request(url, 'POST', headers=self.headers, body=urllib.urlencode(parm))
        return content

    def get(self, url):
        resp, content = httplib2.Http(timeout=15).request(url, headers=self.headers)
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
        #self.logger.debug(next_link)

        # open little war frame and get inuid
        res = self.get(next_link)

        soup = BeautifulSoup(res)
        tags = soup.findAll('param')
        for t in tags:
            m = inu_re.match(t.__str__())
            if m:
                self.inuid = m.group('inuid')
                break
        #self.logger.debug('inuID %s' % self.inuid)

    def work(self):
        # scene recommend
        #scene_recommend = self.get(scenerecommendURL % self.inuid)

        # scene init
        userinfo = json.loads(self.post(scene_init_URL % self.inuid, {'data':'null'}))
        #self.logger.debug('scene init')
        self.logger.debug(userinfo)

        # user info
        self.logger.debug('update user info')
        self.user = User()
        self.user.update(userinfo['info']['player_info'])
        self.user.setTime(userinfo['info']['time'])
        self.user.update_touched_list(userinfo['info']['actionList'])

        self.keyName = userinfo['info']['getKey']['keyName']
        self.key = userinfo['info']['getKey']['key']

        # compute sig
        self.logger.debug('get sig')
        self.requestSig = self.get_sig(self.key, self.keyName)
        #self.logger.debug( self.keyName)
        #self.logger.debug(self.key)
        #self.logger.debug(self.requestSig)

        # friend run
        friendrun = json.loads(self.post_friend_run(self.user.time))
        self.logger.debug('friend run')
        
        # friend list and slave list
        self.user.update_friend_list(friendrun['info']['gameData']['data'])
        self.user.update_slave_list(friendrun['info']['gameData']['slave'])
        #self.user.log()

        # visit myself
        self.logger.debug('my id %d' % self.user.id)
        scenerun = json.loads(self.post_scene_run_without_sig(self.user.id))

        # 0 : Daily reward
        if userinfo['info']['rewardItems'] is not None:
            self.logger.info('daily reward')
            self.post_daily_reward()

        # 1 : Finish personal job at home

        # 1.0 : save main account itself
        #self.save_myself(self.user.id == main_id and len(scenerun['info']['enter_scene']['master_info']) > 0)
        #self.save_myself(self.user.id == last_id and len(scenerun['info']['enter_scene']['master_info']) > 0)

        # 1.1 : Try to use skills
        self.logger.info('check skill')
        self.use_skill(userinfo)
        # 1.2 : Try to harvest both food and soldier
        self.logger.info('check food and soldier')
        self.harvest(scenerun)
        # 1.3 : Kill animals at home
        self.logger.info('check animal')
        self.attack_beasts(scenerun)

        a = time.time()
        # 2 : check friends
        self.logger.info('check friend')
        self.visit_friends()

        # 3 : attack last account
        self.attack_last()
        b = time.time()

        return int(b-a)

    def save_myself(self, b):
        if not b:
            return
        if self.user.population < 100:
            return
        while True:
            self.logger.info('save myself')
            content = json.loads(self.post_defence_riot(self.user.troops_str()))
            self.user.update(content['info']['player_info'])
            if content['info']['riot']['riot_info']['result'] == False:
                self.logger.info('riot success')
                break
            if self.user.population < 10:
                self.logger.info('no enough army')
                break

    def attack_last(self):
        if self.user.id == last_id or self.user.id == main_id:
            return

        if self.user.population < 500:
            return

        # update userinfo first
        content = json.loads(self.post_scene_run(self.user.id))
        self.user.update(content['info']['enter_scene']['player_info'])

        content = json.loads(self.post_scene_run(last_id))
        if len(content['info']['enter_scene']['master_info']) > 0 \
                and content['info']['enter_scene']['master_info']['uid'] == self.user.id:
            return

        if self.user.population == 0:
            return

        self.logger.info('attack last account')
        content = json.loads(self.post_defence_fight(True, self.user.troops_str(), last_id))
        while len(content['info']) > 0 and content['info'].has_key('battleInfo') and content['info']['battleInfo']['attack'].has_key('remainForce') and content['info']['battleInfo']['attack']['remainForce'] != 0:
            time.sleep(0.5)
            content = json.loads(self.post_defence_fight(False, self.user.troops_str(), last_id))
            #self.logger.info(content)

        self.logger.info('attack done')


    def visit_friends(self):
        self.logger.debug('Total %d friends' % len(self.user.friend_list))

        # Go to every friends home
        for friend in self.user.friend_list:
            try:
                self.visit(friend, friend in self.user.slave_list)
            except:
                self.logger.error('timeout')
                continue
            time.sleep(0.5)

    def visit(self, id, is_slave):
        self.logger.debug ('Visiting %d' % id)
        data = self.post_scene_run(id)
        data = json.loads(data)

        # save main account 
        if self.user.id != main_id and id == main_id and len(data['info']['enter_scene']['master_info']) > 0:
            while True:
                self.logger.info('save main account')
                content = json.loads(self.post_defence_help(self.user.troops_str(), id))
                self.user.update(content['info']['player_info'])
                if len(content['info']['master_info']) == 0 or self.user.population < 10:
                    break

        # attack beast
        self.attack_beasts(data)

        if is_slave and (not id in self.user.touched_list) and len(self.user.touched_list) < 4:
            self.logger.info('dong ta yi xia')
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
            self.logger.info('chen huo da jie')
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
                self.logger.debug('ID %d : %d' % (beast['beastId'], beast_cap))
                beast_type[beast['beastId']] = ('unknow animal', beast_cap)

            self.logger.debug('attack %s' % name)
            return True
        else:
            self.logger.debug('no enough population, skip this animal')
            return False

    def use_skill(self, data):
        skillList = data['info']['skillList']

        # YeShouHaoJiao          1
        # TianJiangShenBing      2
        # MiHuanZhiXiang         26
        if self.user.time > skillList['1']['canUseTime']:
            self.post_use_skill(1, self.user.id)
            self.logger.info('YeShouHaoJiao')
        if self.user.time > skillList['26']['canUseTime']:
            self.post_use_skill(26, self.user.id)
            self.logger.info('MiHuanZhiXiang')

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
            time.sleep(0.5)

        for soldier_bulild in soldier_list:
            self.harvest_soldier(soldier_bulild)
            time.sleep(0.5)

    def harvest_food(self, food, food_ids):
        # empty
        if food['start_time'] == 0:
            self.logger.info('produce food')
            self.post_produce_food(food['id'])
        # finish
        elif food['end_time'] < self.user.time:
            # gain food
            self.logger.info('gain food')
            self.post_gain_food(food['id'], food_ids)
            # produce food
            self.logger.info('produce food')
            self.post_produce_food(food['id'])

    def harvest_soldier(self, soldier):
        # empty
        if soldier['start_time'] == 0:
            self.logger.info('try to produce soldier')
            self.post_produce_soldier(soldier['id'])
        # finish
        elif soldier['end_time'] < self.user.time:
            # gain soldier
            self.logger.info('gain soldier')
            self.post_gain_soldier(soldier['id'])
            # produce soldier
            self.logger.info('try to produce soldier')
            self.post_produce_soldier(soldier['id'])

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

    def post_defence_riot(self, troops):
        return self.post(defence_riot_URL % self.inuid, 
                {'keyName':self.keyName, 'data':defence_riot_data % troops, 'requestSig':self.requestSig})

    # Old
    #def post_defence_fight(self, troops, fId):
    #    return self.post(defence_fight_URL % self.inuid,
    #            {'keyName':self.keyName, 'data':defence_fight_data % (troops, fId), 'requestSig':self.requestSig})

    def post_defence_fight(self, first, troops, fId):
        #self.logger.info(self.inuid)
        if first is True:
            return self.post(defence_fight_URL % self.inuid,
                {'keyName':self.keyName, 'data':first_defence_fight_data % (fId, troops), 'requestSig':self.requestSig})
        return self.post(defence_fight_URL % self.inuid,
                {'keyName':self.keyName, 'data':defence_fight_data % fId, 'requestSig':self.requestSig})

    def post_defence_help(self, troops, fId):
        return self.post(defence_help_URL % self.inuid,
                {'keyName':self.keyName, 'data':defence_help_data % (troops, fId), 'requestSig':self.requestSig})

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
        self.logger.info('Start working')
        try:
            """ Start job """ 
            if not self.login() :
                self.logger.error('Login error')
                t = 7140
                return t

            self.logger.info('Login success!')
            self.init()
            t = self.work()
        except:
            self.logger.error('Error ')
            t = 7140
        self.logger.info('Job done') 

        return t

def init_log(name):
    #create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    #logger.setLevel(logging.DEBUG)

    #create file handler and set level to debug
    fh = logging.FileHandler("log")
    fh.setLevel(logging.DEBUG)

    #create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    #add formatter to ch and fh
    fh.setFormatter(formatter)
    #add ch and fh to logger
    logger.addHandler(fh)
    return logger

def single_start(user, password, produce_id = 1, loop = False):
    if not produce_id in range(1,5):
        print 'produce id can be only from 1 to 4'
        return 

    logger = init_log(user)

    while True:
        lw = LittleWar(user, password, produce_id, logger)
        t = lw.start()
        if not loop:
            break
        logger.info('Next job will begin in %d s' % (7200-t))
        #time.sleep(2*60*60 - t + 5)
        if 10*60 - t + 5 < 0:
            time.sleep(5)
        else:
            time.sleep(10*60 - t + 5)

def multiple_start(user_list, password, produce_id = 1, loop = False):
    if not produce_id in range(1,5):
        print 'produce id can be only from 1 to 4'
        return

    for user in user_list:
        t = threading.Thread(target=single_start, args=(user, password, produce_id, loop))
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
