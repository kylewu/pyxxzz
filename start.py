#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             start.py
    Create Date:      Thu Mar 17 10:25:11 2011

'''
import os, time

if __name__ == '__main__':
    user_list = ['wenbin%s@wenbinwu.com' % n for n in ['10', '11', ]]
    password = '111'
    while True:
        for user in user_list:
            cmd = 'python xxzh.py %s %s' % (user, password)
            os.system(cmd)
        time.sleep(2*60*60 + 5*60)
