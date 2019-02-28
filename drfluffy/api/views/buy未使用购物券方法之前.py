from rest_framework.views import APIView
from tools.dictformat import BaseResponse
from rest_framework.response import Response
from api.auth import MyAuth
from api.permissions import MyPermission
import django_redis
from api import models
import json
import logging
import datetime

logger = logging.getLogger(__name__)
CACHE = django_redis.get_redis_connection()


class BuyView(APIView):
    '''结算页面'''
    authentication_classes = [MyAuth, ]
    permission_classes = [MyPermission, ]


    def get(self, request, *args, **kwargs):
        '''结算中心页面'''
        res_obj = BaseResponse()
        user_id = request.user.id
        # 获取缓存中存在的课程列表信息
        checkout_value = CACHE.get(f"BUY_{user_id}")
        if not checkout_value:
            res_obj.code = 2003
            res_obj.msg = "暂无结算数据"
            logger.warning("暂无结算信息")
            return Response(res_obj.dict)
        checkout_list = json.loads(checkout_value)
        res_obj.data = checkout_list
        return Response(res_obj.dict)

    def post(self, request, *args, **kwargs):
        """
        向后端提交要结算的课程的两种方法
        1. 课程详情页面点击 立即购买
        2. 购物车页面 勾选 批量结算
        因此要写个通用的接口,用列表比较好

        格式:
        {
        course_list:[
            {'course_id': 1, 'price_policy_id': 2},
            {'course_id': 2, 'price_policy_id': 4},
        ]
        }
        需要获取的数据：
         课程图片
         课程名称
         课程的价格策略
         课程的优惠券
         该用户的通用优惠券
        """
        # 1获取提交的信息
        res_obj = BaseResponse()
        # 获取用户提交的购买课程列表
        course_list = request.data.get("course_list")
        # 当前的用户id
        user_id = request.user.id
        # 2进行判断
        if not course_list:
            res_obj.code = 2000,
            res_obj.msg = "缺少课程列表course_list参数"
            logger.debug(res_obj.msg)
            return Response(res_obj.dict)
        # 3校验成功,将课程信息存在结算列表中,放入到缓存中去,经过一系列的操作,最后告知用户创建结算成功,前端拿到后就可以跳转到支付页面
        # 结算列表的格式[{课程1的信息包括id,名字.图片价格,和价格策略对应的期限.还有优惠券信息},{课程2...}]
        checkout_list = []
        # 4循环课程列表信息,拿到课程信息.价格信息,以及优惠券信息
        for item in course_list:
            # 获取课程id
            course_id = item.get("course_id")
            price_policy_id = item.get("price_policy_id")
            # 首先判断参数是否提交
            if not (course_id and price_policy_id):
                res_obj.code = 2001
                res_obj.msg = '无效的参数'
                logger.warning('post checkout without course_id and price_policy_id.')
                return Response(res_obj.dict)
            course_obj = models.Course.objects.filter(id=course_id).first()
            if not course_obj:
                res_obj.code = 2002
                res_obj.msg = '无效的课程id'
                return Response(res_obj.dict)
            # 4.1当前课程所有的价格策略
            course_price_policy = course_obj.price_policy.all()
            price_policy_obj = models.PricePolicy.objects.filter(id=price_policy_id).first()
            if not (price_policy_obj and price_policy_obj in course_price_policy):
                res_obj.code = 2003
                res_obj.msg = "无效的价格策略id"
                return Response(res_obj.dict)
            # 4.2创建数据结构存放课程的相关信息及优惠券信息
            course_info = {}
            course_info["id"] = course_obj.id
            course_info["name"] = course_obj.name
            course_info["course_img"] = course_obj.course_img
            course_info["price_policy_id"]=price_policy_obj.id #价格策略id
            course_info["price"] = price_policy_obj.price
            course_info["valid_period_test"] = price_policy_obj.get_valid_period_display()
            # 4.3查询该课程的优惠券
            # 查询的关键点 1. 当前用户 2. 当前课程  3. 未使用.4.优惠券在有效时间内
            #  4.3.1查询该用户下有哪些优惠券记录
            now=datetime.datetime.utcnow()
            coupon_list = models.CouponRecord.objects.filter(
                account=request.user,  # 当前用户
                status=0,  # 未使用的
                coupon__content_type__model='course',  # 跨表操作,找到课程表
                coupon__object_id=course_id,  # 限定哪一个课程
                coupon__valid_begin_date__lte=now,  # 这两个条件保证优惠券在有效时间内
                coupon__valid_end_date__gte=now
            )
            logger.debug(coupon_list)
            #    4.3.2该课程优惠券可用的列表
            curser_coupon_list = []
            for item in coupon_list:
                coupon_dict = {
                    "id":item.coupon.id,  # 优惠券的id
                    "name": item.coupon.name,  # 跨表优惠券的名称
                    "coupon_type": item.coupon.get_coupon_type_display(),  # 优惠券的类型
                    "money_equivalent_value": item.coupon.money_equivalent_value,  # 等值货币
                    "off_percent": item.coupon.off_percent,  # 百分比
                    "minimum_consume": item.coupon.minimum_consume,  # 最低消费
                    # "valid_begin_date":item.coupon.valid_begin_date, # 有效开始时间,json的时候时间不能进行序列化,需要格式化操作
                    "valid_begin_date":datetime.datetime.strftime(item.coupon.valid_begin_date,"%Y-%m-%d %H:%M:%S"), # 有效开始时间
                    "valid_end_date":datetime.datetime.strftime(item.coupon.valid_end_date,"%Y-%m-%d %H:%M:%S"), # 有效结束时间
                }
                # 将优惠券信息加到该课程优惠券列表中
                curser_coupon_list.append(coupon_dict)
            # 4.3.3将课程的的优惠券信息保存到课程字典中
            course_info["curser_coupon_list"] = curser_coupon_list
            # 5将课程信息放入结算列表中
            checkout_list.append(course_info)
        #6通用优惠券
        # 7将结算列表存入缓存中区,由于缓存中存在切记先删除,更新成最新的
        CACHE.delete(f'BUY_{user_id}')
        CACHE.set(f'BUY_{user_id}', json.dumps(checkout_list))
        # 7还有一个通用优惠券
        res_obj.msg = "创建结算成功"
        return Response(res_obj.dict)
