#!/usr/bin/env python
# -*- coding:utf-8 -*-
name = "alex"
ret = f'我的名字是{name}'
print(ret)  # 我的名字是alex
def add(a:int,b:int)->int:  #定义一个函数,告诉其类型,并告诉其返回类型
    print(a+b)
    return a+b

add( 19, 8 ) #27
add(122,123)  #245
add("a","b")