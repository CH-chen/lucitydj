from django.conf.urls import url
from api.views import views
from api.views import account
from api.views import shopping
from api.views import payment

urlpatterns = [
    #第一种
    # url(r'^course/$', views.CourseView.as_view()),
    # url(r'^course/(?P<pk>\d+)/$', views.CourseView.as_view()),
    #第二种和第三种路由匹配list和retrieve
    url(r'^course/$', views.CourseView.as_view({'get':'list'})),
    url(r'^course/(?P<pk>\d+)/$', views.CourseView.as_view({'get':'retrieve'})),

    url(r'^article/$', views.ArticleView.as_view({'get':'list'})),
    url(r'^article/(?P<pk>\d+)/$', views.ArticleView.as_view({'get': 'retrieve'})),

    url(r'^article/(?P<pk>\d+)/agree/$', views.AgreeView.as_view({'get': 'post'})),
    #第一种，继承ViewSetMixin，url对应关系要写
    url(r'^shopping/$', shopping.ShoppingView.as_view({'post': 'create','delete':'destory'})),
    #用第二种，直接继承APiview,不用再写对应关系，直接用自带的用第二种
    url(r'^shoppingcart/$', shopping.ShoppingCartView.as_view()),
    url(r'^pay/$', payment.PayView.as_view()),


    url(r'^author/$', account.AuthorView.as_view()),
    url(r'^center/$', views.CenterView.as_view()),
    # url(r'^article/$', views.ArticleView.as_view()),


]