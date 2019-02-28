from django.conf.urls import url,include
from api.views import course as course_view
from api.views import login as login_view
from api.views import shoppingcart
from api.views import buy
from api.views import pay


urlpatterns = [
    url(r'^courses/$', course_view.CourseListView.as_view()),
    url(r'^courses/category/$', course_view.CourseCategoryView.as_view()),
    url(r'^courses/(?P<pk>\d+)/details-introduce/$', course_view.DetailCourseView.as_view()),
    url(r'^login/$', login_view.LoginView.as_view()),
    # geetest
    url(r'init_geetest/$', login_view.init_geetest),
    #购物车
    url(r'shopping-cart/$',shoppingcart.ShoppingCatView.as_view()),
    #结算
    url(r'buy/$',buy.BuyView.as_view()),
    #支付
    url(r'pay/$',pay.PayView.as_view()),
]