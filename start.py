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
import littlewar

if __name__ == '__main__':
    user_list = ['wenbin%s@wenbinwu.com' % n for n in ['10', '11', '12', '13', '14', '15']]
    password = '1234567'

    littlewar.daemon(user_list, password, 4)
