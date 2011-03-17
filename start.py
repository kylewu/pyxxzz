#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             start.py
    Create Date:      Thu Mar 17 10:25:11 2011

'''
import time
from littlewar import LittleWar

if __name__ == '__main__':
    user_list = ['wenbin%s@wenbinwu.com' % n for n in ['10', '11', '12', '13', '14', '15']]
    password = 'abcdefg'
    while True:
        print 'Start working'
        for user in user_list:
            lw = LittleWar(user, password)
            lw.start()
        print 'Job done, waiting for next job'
        time.sleep(2*60*60 + 5*60)
