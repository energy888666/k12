#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework.filters import BaseFilterBackend
import logging
logger=logging.getLogger(__name__)
class MyFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        #从url上获取用户的id,
        category_id = str(request.query_params.get("sub_category",""))
        logger.debug(f'课程分类id:{category_id}')
        #如果category_id是0 或者不是数子就返回所有的课程
        if category_id!="0" and category_id.isdigit():
            queryset=queryset.filter(course_category_id=int(category_id))
        return queryset

