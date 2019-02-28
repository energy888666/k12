#!/usr/bin/env python
# -*- coding:utf-8 -*-
# import traceback
# def func(a,v):
#
#     print(a/v)
#
# if __name__ == '__main__':
#     try:
#         func(10,0)
#     except ZeroDivisionError as e:
#
#         print(e)
#         value=traceback.format_exc()
#         print(value)
#     except Exception as e:
#         print(e,type(e))

# class People(object):
#     __slots__ = ("name","age")  #定义类中只能有 name 和age 属性
#     def __init__(self,name,age):
#         self.name=name
#         self.age=age
# p1=People('alex',19)
# # 正常为{'name': 'alex', 'age': 19},假如定义了__slots__,此时在执行__dict__将会报错
# print(p1.__dict__)
# p1.name='alex2'
# #不加上__slots__ 此时最后打印结果为 alex2 和120
# p1.id=120
# print(p1.name,p1.id) #将会报错,定义类中只能有name和age字段

# a = 1
# b =2
# a, b = b ,a
# print( a,b)
# print(range(5),type(range(5)))
# x = range(5)
# print(dir(x))
# # print(xrange(5),type(xrange(5)))
# with open("./manage.py",mode="r",encoding="utf-8") as f:
#     x=f.readlines()
#     x=f.xre
#     for i in x:
#         print(i)

import logging

# logging.basicConfig(filename='app.log',
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(module)s: %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S',
#                     level=40)    # level 设置级别. 当你的信息的级别>=level的时候才会写入日志文件, 默认30
#
# # CRITICAL = 50
# # FATAL = CRITICAL
# # ERROR = 40
# # WARNING = 30
# # WARN = WARNING
# # INFO = 20
# # DEBUG = 10
# # NOTSET = 0
# # 写日志
# # logging.critical("我是critical")
# # logging.error("我是error")
# # logging.warning("我是警告")
# # logging.info("我是基本信息")
# # logging.debug("我是调试")
# # logging.log(2, "我是自定义")

# import traceback,logging
# logging.basicConfig(filename='x1.txt',
#                     format='%(asctime)s - %(name)s - %(levelname)s -%(module)s: %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S',
#                     level=30) # 当设置级别.当你的信息的级别>=level的时候才会写入日志文件, 默认30
# for i in range(5):
#     try:
#         if i % 3 == 0:
#             raise FileNotFoundError("我是FileNotFountException")
#         elif i % 3 == 1:
#             raise StopIteration()
#         elif i % 3 == 2:
#             raise KeyError()
#
#     except FileNotFoundError as e:
#         val = traceback.format_exc()
#         logging.error(val)
#     except StopIteration as e:
#         val = traceback.format_exc()
#         logging.error(val)
#     except KeyError as e:
#         val = traceback.format_exc()
#         logging.error(val)
#     except Exception as e:
#         val = traceback.format_exc()
#         logging.error(val)


# 多文件日志处理
# 创建一个操作日志的对象logger（依赖FileHandler）
# file_handler = logging.FileHandler('l1.log', 'a', encoding='utf-8')
# # 设置日志文件内容的格式
# file_handler.setFormatter(logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s -%(module)s: %(message)s"))
# logger1 = logging.Logger('A', level=40)
# logger1.addHandler(file_handler)
# # 记录日志
# logger1.error('我是A系统')
#
# # 再创建一个操作日志的对象logger（依赖FileHandler）
# file_handler2 = logging.FileHandler('l2.log', 'a', encoding='utf-8')
# file_handler2.setFormatter(logging.Formatter(fmt="%(asctime)s - %(name)s -%(levelname)s -%(module)s: %(message)s"))
# logger2 = logging.Logger('B', level=40)
# logger2.addHandler(file_handler2)
# # 记录日志
# logger2.error('我是B系统')

# for m in range(1,10):
#     for n in range(1,m+1):
#         print("%s * %s = %d" %(m,n,m*n),end=" ")
#     print("")
# dic ={1:"nihao",5:"haha"}
# if 1 in dic:
#     print(111)
# for i in []:
#     print(1)
# lst=[
#                 {
#                     "id": 5,
#                     "valid_period": 90,
#                     "valid_period_text": "3个月",
#                     "default": True,
#                     "prcie": 333
#                 },
#                 {
#                     "id": 1,
#                     "valid_period": 999,
#                     "valid_period_text": "永久有效",
#                     "default": True,
#                     "prcie": 999
#                 }
#             ]
# lst2=[i["id"] for i in lst]
# print(lst2)


