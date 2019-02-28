#!/usr/bin/env python
# -*- coding:utf-8 -*-
from api import models
from rest_framework.response import Response
from  rest_framework.generics import ListAPIView,RetrieveAPIView
from api.serilalizers.course import CourseModelserializer,CourseCategoryModelserizlizer,DetailCourseModelserizlizer
from tools.dictformat import BaseResponse
from api.myfilter import MyFilter
import logging
from api.auth import MyAuth
from api.permissions import MyPermission
# 实例化log对象 --> logger
# 以当前文件的名字作为logger实例的名字
logger = logging.getLogger(__name__)
# 生成一个 名字叫 collect 的日志实例,在settings中提前配置好,用于收集用户的信息,例如你访问过手机品类的信息,下次一直给你推送手机的信息
# logger_c = logging.getLogger("collect")
# 课程列表
class CourseListView(ListAPIView):
    queryset = models.Course.objects.all()
    serializer_class = CourseModelserializer
    filter_backends = [MyFilter,]
    # authentication_classes =[MyAuth,]
    #课程列表需要登录后才能访问
    # permission_classes = [MyPermission,]
    def get(self,request,*args,**kwargs):
        res_obj=BaseResponse()
        try:
            queryset = self.filter_queryset(self.get_queryset())
            # 手动过滤
            # 拿到过滤的条件
            # category_id = str(request.query_params.get('category', ''))
            # logger.debug(f'category_id:{category_id}')
            # # 如果category_id是0或者不是数字 我们就返回所有的课程
            # if category_id != '0' and category_id.isdigit():
            #     # 按照条件去过滤
            #     queryset = queryset.filter(course_category_id=category_id)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            res_obj.data = serializer.data
            data = serializer.data
            # 因为要排序的字段是我们序列化的时候自己加的字段，不能使用内置的order_by
            # 进行分类排序
            ordering_key = request.query_params.get("ordering", "")
            logger.debug(f'排序:{ordering_key}')
            if ordering_key:
                if ordering_key.startswith("-"):
                    ordering_key = ordering_key[1:]
                    is_reverse = True
                else:
                    is_reverse = False
                    # 对返回的数据进行排序
                data = sorted(data, key=lambda dict: dict.get(ordering_key, 0), reverse=is_reverse)
            res_obj.data = data
        except Exception as e:
                res_obj.code=1
                res_obj.msg=str(e)
                # logger.debug(str(e)) # debug 级别为10,配置的级别如果高于他,将不会写入文件
                logger.error(str(e)) #error 级别为40 #INFO = 20,waring=30
        return Response(res_obj.dict)

#课程分类序列化
class CourseCategoryView(ListAPIView):
    queryset = models.CourseCategory.objects.all()
    serializer_class = CourseCategoryModelserizlizer

    def get(self,request,*args,**kwargs):
        res_obj=BaseResponse()
        try:

            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            res_obj.data=serializer.data
        except Exception as e:
            res_obj.code=2
            res_obj.msg=str(e)
        return Response(res_obj.dict)

#课程详情
class DetailCourseView(RetrieveAPIView):
    queryset = models.CourseDetail.objects.all()
    serializer_class = DetailCourseModelserizlizer

    def get(self, request, *args, **kwargs):
        res_obj=BaseResponse()
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            res_obj.data=serializer.data
        except Exception as e:
            logger.debug(str(e))
            res_obj.code=3
            res_obj.msg=str(e)
        return Response(res_obj.dict)




