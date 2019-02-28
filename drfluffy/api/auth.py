from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api import models
import datetime
from django.conf import settings
from django.core.cache import cache
class MyAuth(BaseAuthentication):
    def authenticate(self, request):
        #获取用户带来的token
        # print(request.META.get("HTTP_AUTHORIZATION",""))
        token=request.META.get("HTTP_AUTHORIZATION","")

        # 先从缓存中取
        user_obj = cache.get(token)
        # 缓存中能取到当前登录的用户就直接从缓存取
        if user_obj:
            return user_obj, token

        # 缓存中获取不到,再从数据库中获取
        # 判断是否有
        if token:
            # 进行验证token
            token_obj=models.Token.objects.filter(key=token).first()
            if token_obj:
                # 判断token是否有效
                timeout_seconds = settings.AUTH_TOKEN_TIMEOUT  # 秒数
                # 拿到当前时间
                now = datetime.datetime.now(tz=datetime.timezone.utc)
                #获取创建token时的时间
                token_time=token_obj.created
                # 不同时区不能直接相减,及其改变成浮点数
                # print((now - token_time).total_seconds())
                is_ok=(now-token_time).total_seconds()<timeout_seconds
                if is_ok:
                    #没过期
                    user_obj = token_obj.user
                    return user_obj, token
                else:
                    raise AuthenticationFailed("token已经过期了")
            else:
                raise AuthenticationFailed("无效的token")
        else:
            raise AuthenticationFailed("请求的URL中必须携带token参数")

