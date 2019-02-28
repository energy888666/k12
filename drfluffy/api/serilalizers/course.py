from api import models
from rest_framework import serializers

#价格序列化
class PirceModelserializer(serializers.ModelSerializer):
    class Meta:
        model=models.PricePolicy
        fields="__all__"

#课程序列化

class CourseModelserializer(serializers.ModelSerializer):

    # price=serializers.SerializerMethodField(read_only=True)
    # order_details=serializers.SerializerMethodField(read_only=True)
    order_details=serializers.IntegerField(source='order_details.count',read_only=True)

    # def get_price(self,obj):
    #     # 把所有课程永久有效的价格拿出来
    #     price_obj=obj.price_policy.all().filter(valid_period=999).first()
    #     return price_obj.price

    # def get_order_details(self,obj):
    #     return obj.order_details.count()
    # 修改序列化结果serialize,data的终极方法
    def to_representation(self, instance):
        # return "嘿嘿"   #什么都不写直接返回,此时 serialize.data序列话后都是嘿嘿
        # 下面要继承父类的方法,然后做额外的操作
        # 此时的data 就是serializer.data(序列化后拿到的数据为OrderedDict)
        data=super(CourseModelserializer, self).to_representation(instance)
        # print(data)
        # 针对序列化的结果做一些自定制操作
        # 判断当前这个课程是否有永久有效的价格
        price_obj = instance.price_policy.all().filter(valid_period=999).first()
        if price_obj:
            # 有永久有效的价格
            data['has_price'] = True
            data['price'] = price_obj.price
        else:
            # 没有永久有效的价格策略
            data['has_price'] = False
        return data

    class Meta:
        model=models.Course
        fields="__all__"

#课程分类列表序列化
class CourseCategoryModelserizlizer(serializers.ModelSerializer):

    class Meta:
        model=models.CourseCategory
        fields="__all__"


 #讲师
class TeacherModelserizlizer(serializers.ModelSerializer):

    class Meta:
        model=models.Teacher
        fields="__all__"


#课程详情
class DetailCourseModelserizlizer(serializers.ModelSerializer):
    course_info=serializers.SerializerMethodField(read_only=True)
    teachers_info=serializers.SerializerMethodField(read_only=True)


    def get_teachers_info(self,obj):
        return TeacherModelserizlizer(obj.teachers.all(),many=True).data

    def get_course_info(self,obj):
        return CourseModelserializer(obj.course).data

    class Meta:
        model=models.CourseDetail
        fields="__all__"
        extra_kwargs={
           "course" :{"write_only":True},
           "teachers" :{"write_only":True}
        }