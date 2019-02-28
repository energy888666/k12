
  # 路飞项目自定义一个抛异常的方法
class PayException(Exception):
    def __init__(self,code,msg):
        self.code=code
        self.msg=msg
    def __str__(self):
        return self.msg