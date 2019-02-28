from django.shortcuts import HttpResponse
from api import models
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from tools.dictformat import BaseResponse
import uuid
import datetime
from django.core.cache import cache
from django.conf import settings
#引入滑动验证
from tools.geetest import GeetestLib
import logging
logger=logging.getLogger(__name__)

#请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"
mobile_geetest_id = "7c25da6fe21944cfe507d2f9876775a9"
mobile_geetest_key = "f5883f4ee3bd4fa8caec67941de1b903"

# 初始化滑动验证码的接口
def init_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    # request.session[gt.GT_STATUS_SESSION_KEY] = status
    # request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)


class LoginView(APIView):

    def post(self, request, *args, **kwargs):
        res_obj=BaseResponse()

        #滑动验证的代码,获取用户提交的验证码
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.data.get(gt.FN_CHALLENGE, '')
        validate = request.data.get(gt.FN_VALIDATE, '')
        seccode = request.data.get(gt.FN_SECCODE, '')
        status = True
        if status:
            # 调用极验科技的接口检验是不是真人
            result = gt.success_validate(challenge, validate, seccode, None)
        else:
            # 本地校验是不是正经人
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            username = request.data.get("username")
            password = request.data.get("password")
            ##使用内置的auth模块提供的authenticate方法校验用户名密码是否正确(密码是加过密的)
            user_obj = authenticate(username=username, password=password)
            if user_obj:
                logger.debug("用户名密码正确")
                # logger最好接受一个参数,接收两个将会出现报错信息
                # logger.debug(res_obj,user_obj)
                # 创建Token
                token=uuid.uuid1().hex
                #当前时间
                now=datetime.datetime.now(tz=datetime.timezone.utc)
                # 设置到库中
                # ? 不是简单地创建，如果当前用户有token就更新 没有才创建新的
                # models.Token.objects.create(key=token, user=user_obj, created=now)
                obj,created=models.Token.objects.update_or_create(user=user_obj,defaults={"key":token,"created":now})
                #将token设置到缓存中,读取方便:
                cache.set(token,user_obj,settings.AUTH_TOKEN_TIMEOUT)


                #返回token
                res_obj.data=token

            else:
                logger.debug('用户名和密码错误')
                res_obj.code=20
                res_obj.msg="用户名或密码错误"
        else:
            res_obj.code=10
            res_obj.msg="请滑动验证码进行校验"
        return Response(res_obj.dict)