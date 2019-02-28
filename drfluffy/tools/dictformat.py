
class BaseResponse(object):
    __slots__ = ("code","data","msg")

    def __init__(self):
        self.code=0
        self.data=None
        self.msg=''

    @property
    def dict(self):
        return {"code":self.code,"data":self.data,"msg":self.msg}

if __name__ == '__main__':
    res_obj=BaseResponse()
    res_obj.code=0
    res_obj.data={1:2,3:4}
    res_obj.msg="错误"
    print(res_obj.dict)
    print(res_obj.__dict__)