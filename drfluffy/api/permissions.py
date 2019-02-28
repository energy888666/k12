#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework.permissions import BasePermission
import logging
logger=logging.getLogger(__name__)
class MyPermission(BasePermission):
    def has_permission(self, request, view):
        #判断用户是否登录
        if request.auth:
            # logger.debug(request.auth)
            # logger.debug(request.user)
            return True
        else:
            # print(request.auth)
            return False