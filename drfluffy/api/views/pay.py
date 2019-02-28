#!/usr/bin/env python
# -*- coding:utf-8 -*-
from rest_framework.views import APIView
from tools.dictformat import BaseResponse
from tools.exception import PayException
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


class PayView(APIView):
    """支付校验"""
    authentication_classes = [MyAuth, ]
    permission_classes = [MyPermission, ]

    def _clac_coupon_price(self, o_price, coupon_record_obj):
        """
        计算券后价格
        :param o_price: 原价格
        :param coupon_obj: 优惠券对象（课程优惠券/通用优惠券）
        :return: 券后价格
        """
        if coupon_record_obj.coupon.coupon_type ==0:
            # 立减券
            course_coupon_price = o_price -coupon_record_obj.coupon.money_equivalent_value
            if course_coupon_price<0:
                course_coupon_price=0
        elif coupon_record_obj.coupon.coupon_type ==1:
            #满减券
            if o_price<coupon_record_obj.coupon.minimum_consume:
                raise PayException(3004,"该课程价格不可以使用满减券")
            course_coupon_price = o_price -coupon_record_obj.coupon.money_equivalent_value
        elif coupon_record_obj.coupon.coupon_type ==2:
            course_coupon_price= o_price * coupon_record_obj.coupon.off_percent/100
        else:
            logger.error("应该不会到这来")
            raise PayException(500,"内部错误")
        return course_coupon_price


    def post(self,request,*args,**kwargs):
        """
          对前端传过来的数据进行校验
          格式如下
          {
              "use_beli":false/true,  贝里
              "course_list":[{ 课程列表
                  "course_id":1,  课程的id
                  "price_policy_id":1,课程价格策略id
                  "coupon_record_id":2 优惠券id
              },
              {
                  "course_id":2,
                  "price_policy_id":4
              }],
              "common_coupon_id":3,通用优惠券的id
              "pay_money":298 总价钱
          }
          """
        res_obj = BaseResponse()
    # TODO 1.获取数据
        user_id = request.user.id
        use_beli= request.data.get("use_beli")
        course_list = request.data.get("course_list")
        common_coupon_id = request.data.get("common_coupon_id",) #通用优惠券
        pay_money = request.data.get("pay_money")
        now=datetime.datetime.utcnow()

    # TODO 2.对数据进行校验
        # 2.1对课程id进行校验
        course_coupon_price_list = []  # TODO 定义一个列表用来存放每个课程经过用课程优惠券的后价格
        try:
            if not (course_list and f"{use_beli}" and pay_money):
                raise PayException(3000,"提交的信息不全")
            for item in course_list:
                # 获取相关的数据
                course_id=item.get("course_id")
                # print(course_id)
                price_policy_id=item.get("price_policy_id")
                coupon_record_id=item.get("coupon_record_id")
                course_obj = models.Course.objects.filter(id = course_id).first()

                if not course_obj:
                    logger.warning(f'用户：{user_id} 支付 课程：{course_id} 不存在')
                    raise PayException(3001,"支付的的课程id不存在")
        # 2.2对价格策略id进行校验(是否是该课程的)
                price_policy_obj = models.PricePolicy.objects.filter(
                    id = price_policy_id,  # 价格策略id
                    object_id=course_id,  # 课程id
                    content_type__model="course" # 课程表
                ).first()
                if not price_policy_obj:
                    logger.warning(f'用户：{user_id} 支付 课程：{course_id} 的价格策略{price_policy_id} 不存在')
                    raise PayException(3002,"无效的价格策略")
        # 2.3对课程的优惠券进行校验
        # 只有勾选课程优惠券才走下面的判断及结算课程券后价格
                course_origin_price=price_policy_obj.price  # 课程原价
                course_coupon_price = course_origin_price #TODO 假如无优惠券此时就是原来的价格
                if coupon_record_id:
                    coupon_record_obj = models.CouponRecord.objects.filter(
                        id = coupon_record_id,
                        account=request.user,
                        status = 0,
                        coupon__content_type__model="course",  # 限定查哪张表
                        coupon__object_id=course_id,  # 限定哪一个课程
                        coupon__valid_begin_date__lte=now,
                        coupon__valid_end_date__gte=now,
                    ).first()

                    if not coupon_record_obj:
                        logger.warning(f'用户：{user_id} 支付 课程：{course_id} 的优惠券{coupon_record_id} 不存在')
                        raise PayException(3003,"无效的优惠券id")
                    # TODO 使用了课程的优惠券 还需要计算课程券后价格
                    #  TODO 根据优惠券的类型不同 按照不同的规则计算券后价格
                    course_coupon_price = self._clac_coupon_price(course_origin_price,coupon_record_obj)
                    print('#' * 60)
                    print(f'课程名称：{course_obj.name} 原价：{course_origin_price} 券后价：{course_coupon_price}')
                course_coupon_price_list.append(course_coupon_price) #TODO 将所有课程价格加入到到总列表中(用过课程券后的)
            sum_course_price=sum(course_coupon_price_list) # 所有课程的总券后价
        # 2.4对通用的优惠券进行校验
            if common_coupon_id: #只有使用了通用优惠券才会向下走
                print("2" * 120)
                common_record_obj = models.CouponRecord.objects.filter(
                    id=common_coupon_id,
                    account=request.user,
                    status=0,
                    coupon__content_type__model="course",  # 限定哪一门课程
                    coupon__object_id=None,  # 通用的券
                    coupon__valid_begin_date__lte=now,
                    coupon__valid_end_date__gte=now
                ).first()
                print("*" * 120,common_record_obj)
                if not common_record_obj:
                    print(f'用户：{user_id} 通用券：{common_coupon_id}不存在')
                    raise PayException(3005,"通用券无效")
                common_price=self._clac_coupon_price(sum_course_price,common_record_obj) #算出来使用通用券后的总价格
            else:
                common_price = sum_course_price
            print('*' * 120)
            print(f'初始总价：{sum_course_price} 券后总价：{common_price}')
        # 2.5对用户的贝里进行校验
            if use_beli:
                my_beli=request.user.beli/10
                if my_beli>common_price:
                    request.user.beli=(my_beli-common_price) * 10
                    result_price=10
                    cost_beli=common_price * 10
                else:
                    result_price=common_price-my_beli
                    request.user.beli=0
                    cost_beli =my_beli*10  # TODO 记录消费了多少贝里,如果订单取消或超时未支付,再返回来.
                request.user.save() #TODO 此时需要修改数据库,如果取消了订单在给用户返回,不这样的话,他在多个订单都可以使用贝里
            else:
                result_price = common_price
                cost_beli=0

         # 2.6对价格进行校验
            if pay_money != result_price:
                logger.warning(f"用户{user_id}支付异常")
                raise PayException(3006,"支付异常")
            else:
                res_obj.msg="支付成功"
                return Response(res_obj.dict)

        except PayException as e:
            res_obj.code=e.code
            res_obj.msg=e.msg
        except Exception as e:  # 一般不会走到这的
            res_obj.code = 500
            res_obj.msg = str(e)
            logger.error(str(e))
        return Response(res_obj.dict)
        # TODO 3.生成订单
    # TODO 4 .拼接url
        pass