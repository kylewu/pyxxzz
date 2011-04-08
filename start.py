#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

    Author:
        Wenbin Wu <admin@wenbinwu.com>
        http://www.wenbinwu.com
 
    File:             start.py
    Create Date:      Thu Mar 17 10:25:11 2011

'''
import littlewar

if __name__ == '__main__':
    user_list = ['wenbin%s@wenbinwu.com' % n for n in ['10', '11', '12', '13', '14', '15']]
    user_list.append('wenbin@wenbinwu.com')
    #user_list = ['wenbin14@wenbinwu.com']
    password = ''
    my_ids = [59094425,355852754,356032671,356151199,356298870,356527009,356837352]

    littlewar.multiple_start(user_list, password, produce_id=1, logfile='log', loop=True)
