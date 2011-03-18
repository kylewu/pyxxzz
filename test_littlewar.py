#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             test_littlewar.py
    Create Date:      Thu Mar 17 22:29:33 2011

'''
from littlewar import LittleWar
import simplejson as json

def check_sig():
    key = "9eeb28f7617b482ab001f67043b3e177"
    keyName = "a548d6aefbeb32e0"
    requestSig='fc5e065b5c9b3bc528fad54a195533ee'

    lw = LittleWar()
    print lw.get_sig(key, keyName)
    if lw.get_sig(key, keyName) == requestSig:
        print 'ok'

def test_json():
    f = open('attack_return')
    str = f.read(999999)
    j = json.loads(str)
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

def test_spycase():
    str = ' {"result":0,"method":"spy.sentSpy","msg":"","info":{"placeId":0,"result":1,"levelUp":[],"cupResult":[],"achCupResult":null}}'
    str = json.loads(str)
    print str['info']
    if str['info'].has_key('player_info'): # success in sending a spy
        print 'sucess'
test_spycase()

#test_json()
#check()
