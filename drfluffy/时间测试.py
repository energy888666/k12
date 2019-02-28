#!/usr/bin/env python
# -*- coding:utf-8 -*-
import datetime
import time
#
# now=datetime.datetime.utcnow()
# print(now)
# time.sleep(5)
# now2=datetime.datetime.now()
# print(now2)
# print(now2-now)
now=datetime.datetime.now()
now2=datetime.datetime.strftime(now,"%Y-%m-%d %H:%M:%S")
# print(now,type(now2))   # 2019-01-24 09:58:56.644907 <class 'str'>

stime="2019-01-24 09:58:56"
now3=datetime.datetime.strptime(stime,"%Y-%m-%d %H:%M:%S")
# print(now3,type(now3))  # 2019-01-24 09:58:56 <class 'datetime.datetime'>
#sum测试
# lst=[1,2,3,4,5,6]
# print(sum(lst))

print(sum((1,),4))
