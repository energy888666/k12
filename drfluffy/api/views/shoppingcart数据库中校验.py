from rest_framework.views import APIView
from rest_framework.response import Response
from tools.dictformat import BaseResponse
import redis
from api.auth import MyAuth
from api.permissions import MyPermission
from api import models
import django_redis
import json
import logging
logger=logging.getLogger(__name__)
CACHE=django_redis.get_redis_connection()
class ShoppingCatView(APIView):
    authentication_classes = [MyAuth,] #认证
    permission_classes = [MyPermission,] #权限
    #展示购物车页面
    def get(self,request,*args,**kwars):
        # 从缓存中读取当前用户的购物车
        shopping_cat_value=CACHE.get(f'SHOPPING_CAT_{request.user.id}')
        #判断是否存在
        if shopping_cat_value:
            #反序列化
            shopping_cat_lst=json.loads(shopping_cat_value)
            logger.debug(shopping_cat_lst)
        else:
            shopping_cat_lst=[]
        res_obj=BaseResponse()
        res_obj.data=shopping_cat_lst
        return Response(res_obj.dict)

    def post(self,request,*args,**kwargs):
        res_obj=BaseResponse()

        # 1.先获取用户提交的数据包括,用户id,(课程id,图片,标题),(价格策略,价格)
        # 获取课程的id
        course_id=request.data.get("course_id")
        #获取价格策略的id
        price_policy_id=request.data.get("price_policy_id")
        #获取用户的id
        user_id=request.user.id
        # 2. 校验数据的有效性
        # 2.1对课程id进行校验
        course_obj=models.Course.objects.filter(id=course_id).first()
        if not course_obj:
            res_obj.code = 1000
            res_obj.msg="无效的课程id"
            return Response(res_obj.dict)
         #2.2对价格策略的有效性进行校验,找到课程对应的价格策略
        price_policy_obj=models.PricePolicy.objects.filter(id=price_policy_id).first()
        #当前课程所有的价格策略
        course_price_policy=course_obj.price_policy.all()
        if not(price_policy_obj and price_policy_obj in course_price_policy):
            res_obj.code = 1002
            res_obj.msg="无效的价格策略"
            return Response(res_obj.dict)
        #先获取当前用户购物车已有的数据
        shopping_cat_value=CACHE.get(f'SHOPPING_CAT_{user_id}')
        if shopping_cat_value:
            shopping_cat_lst=json.loads(shopping_cat_value)  # 能取到就把redis中存储的数据反序列化成列表
            # logger.debug(shopping_cat_lst)
        else:
            shopping_cat_lst=[] # 取不到就生成一个空列表
        # 3. 把购物车页面用到的数据都查出来
        # 3.1 把课程所有的价格策略取出来
        price_list=[]
        #拿到课程所有的价格策略
        for item  in course_price_policy:
            price_list.append({
                "id":item.id,
                "valid_period":item.valid_period,
                "valid_period_text":item.get_valid_period_display(),
                "default":True if str(item.id)==price_policy_id else False,
                "prcie":item.price
            })
        courser_info={}
        courser_info["id"]=course_id
        courser_info["default_price_period_id"]=price_policy_id  #默认选中的价格策略id
        courser_info["default_price_period"]=price_policy_obj.get_valid_period_display()  #有效时间
        courser_info["default_price"]=price_policy_obj.price #默认的价格
        courser_info["relate_price_policy"]=price_list #价格策略
        # logger.debug(courser_info)
        # 4.判断购物车是否已有该课程
        for i in shopping_cat_lst:
            # logger.debug(type(courser_info["id"]))
            # logger.debug(i)
            if courser_info["id"] ==i["id"]:
                res_obj.code=1003;
                res_obj.msg="该购物车已存在该课程"
                return Response(res_obj.dict)
        #5.没有该课程加入购物车,并放在内存中
        shopping_cat_lst.append(courser_info)  # 把当前这个课程加入购物车列表
        # CACHE.set(f'SHOPPING_CAT_{user_id}',courser_info) #不能放字典,只能放字符串或者数字
        CACHE.set(f'SHOPPING_CAT_{user_id}',json.dumps(shopping_cat_lst))

        res_obj.msg="加入购物车成功"
        return Response(res_obj.dict)

    def put(self,request,*args,**kwargs):
        res_obj=BaseResponse()
        '''更新购物车'''
        # 1.获取用户更新的信息
        # 获取用户提交的课程id
        course_id=request.data.get("course_id")
        #获取更新的价格策略的id
        price_policy_id=request.data.get("price_policy_id")
        # 获取用户的id
        user_id = request.user.id
        # 2判断是否有效
        if not(course_id and price_policy_id):
            res_obj.code = 1004
            res_obj.msg = '没有参数'
            logger.warning('shopping cart put without course_id and price_policy_id.')
            return Response(res_obj.dict)
        # 判断课程id是否有效
        course_obj=models.Course.objects.filter(id=course_id).first()
        if not course_obj:
            res_obj.code=1005; #更新时,课程id不存在
            res_obj.msg="更新的课程id不存在"
            return  Response(res_obj.dict)
        # 获取课程对应所有的价格策略
        course_price_policy=course_obj.price_policy.all()
        # 判断课程的价格策略是否有效
        price_policy_obj=models.PricePolicy.objects.filter(id=price_policy_id).first()
        if not(price_policy_obj and price_policy_obj in course_price_policy):
            res_obj.code = 1006;  # 更新时,该课程id不存在该价格策略
            res_obj.msg = "价格策略id不合法"
            return Response(res_obj.dict)
        # 3.从内存中获取数据进行更新
        shopping_cat_value=CACHE.get(f'SHOPPING_CAT_{user_id}')
        # 判断内存中该购物车是否有课程
        if not shopping_cat_value:
            res_obj.code = 1007;  # 更新时,购物车是空的
            res_obj.msg = "您的购物车为空,无法进行更新"
            logger.debug(res_obj.msg)
            return Response(res_obj.dict)
        #有的话进行序列化
        shopping_cat_list=json.loads(shopping_cat_value)
        #然后进行修改
        for item in shopping_cat_list:  #循环购物车列表
            if str(item["id"])==course_id:  #找到要修改的课程id,修改价格策略
                item["default_price_period_id"] = price_policy_id  # 修改更新价格策略id
                item["default_price_period"] = price_policy_obj.get_valid_period_display()  # 有效时间
                item["default_price"] = price_policy_obj.price  # 修改的价格
                #循环该课程价格策略,修该默认选中:
                for i in item["relate_price_policy"]:
                    if str(i["id"])==price_policy_id:
                        i["default"]=True
                    else:
                        i["default"]=False
                res_obj.msg="修改成功"
                #并在内存中进行修改
                CACHE.set(f'SHOPPING_CAT_{user_id}',json.dumps(shopping_cat_list))
                return Response(res_obj.dict)
        else:
            res_obj.code=1008
            res_obj.msg="您的购物车列表无要修改的课程id"
            return  Response(res_obj.dict)


    def delete(self,request,*args,**kwargs):
        '''删除购物车'''
        res_obj=BaseResponse()
        # 1获取信息
        course_id=request.data.get("course_id")
        user_id=request.user.id
        #2进行课程的校验
        if not course_id:
            res_obj.code=1009
            res_obj.msg="无效的课程id"
            return Response(res_obj.dict)
        course_obj=models.Course.objects.filter(id=course_id).first()
        #3从内存中获取并进行修改
        shopping_cat_value = CACHE.get(f'SHOPPING_CAT_{user_id}')
        if shopping_cat_value:
            shopping_cat_lst = json.loads(shopping_cat_value)
        else:
            shopping_cat_lst=[]
        #对购物车列表进行遍历删除course_id对应的课程,不能循环列表进行删除
        shopping_cat_num=len(shopping_cat_lst)
        for i in range(shopping_cat_num):
            if shopping_cat_lst[i]["id"]==course_id:
                shopping_cat_lst.pop(i)
                res_obj.msg="删除课程成功"
                # 删除成功后更新缓存
                CACHE.set(f'SHOPPING_CAT_{user_id}',json.dumps(shopping_cat_lst))
                return Response(res_obj.dict)
        else:
            #要删除的课程不再购物车里
            res_obj.code=1010
            res_obj.msg="要删除的课程不再购物车里"
            return  Response(res_obj.dict)


'''
data": [
        {
            "id": "1",
            "default_price_period_id": "1",
            "default_price_period": "永久有效",
            "default_price": 999,
            "relate_price_policy": [
                {
                    "id": 5,
                    "valid_period": 90,
                    "valid_period_text": "3个月",
                    "default": false,
                    "prcie": 333
                },
                {
                    "id": 1,
                    "valid_period": 999,
                    "valid_period_text": "永久有效",
                    "default": true,
                    "prcie": 999
                }
            ]
        },
        {
            "id": "2",
            "default_price_period_id": "2",
            "default_price_period": "永久有效",
            "default_price": 777,
            "relate_price_policy": [
                {
                    "id": 2,
                    "valid_period": 999,
                    "valid_period_text": "永久有效",
                    "default": true,
                    "prcie": 777
                }
            ]
        }
    ]
'''