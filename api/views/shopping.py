from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet,ViewSetMixin,ModelViewSet,mixins
from rest_framework import serializers
from api import models
from api.auth.auth import LuAuth
from django.core.exceptions import ObjectDoesNotExist
from utils.exception import PriceInvalid
from django_redis import get_redis_connection
from lucitydj import settings
import json

#第一种，继承与ViewSetMixin，URL中对应关系要写
class ShoppingView(ViewSetMixin,APIView):
    authentication_classes = [LuAuth,]
    conn =  get_redis_connection("default")  #下面调用要加self
    def create(self,request,*args,**kwargs):
        ret = {"code":1000,"data":None}


        try:
            print(request.data)
            #1.获取课程id和价格id要用int转化一下，数据库的id是数字，用户可能发的是字符串
            course_id = int(request.data.get("courseid"))
            price_id = int(request.data.get("priceid"))
            #2.获取专题课课程信息******
            course = models.Course.objects.get(id=course_id)
            #3.获取课程的价格策略********
            price_list = course.price_policy.all()
            print(price_list)
            price_dict = {}
            for item in price_list:
                # print(item.id)
                # print(item.valid_period)
                # print(item.get_valid_period_display())
                # print(item.price)
                price_dict[item.id]={
                    "period":item.valid_period,
                    "period_display":item.get_valid_period_display(),
                    "price":item.price
                }
            print(price_dict)
            #4.判断用户输入的价格策略是否合法
            if price_id not in price_dict:
                # ret["code"] = 2000  #第一种返回错误信息
                # ret["error"] = "价格不合法"
                raise PriceInvalid("价格不合法") #第二种自定义异常
            #5.将购物信息添加到购物车
            # cart_key = "chen_shopping_cart_%s_%s"
            print(request.auth.user_id)
            cart_key = settings.SHOPPING_CART_KEY %(request.auth.user_id,course_id,)
            print(cart_key)
            cart_dict = {
                'title':course.title,
                'img':course.course_img,
                'default_price':price_id,
                'price':json.dumps(price_dict)
            }
            print(cart_dict)
            # conn = get_redis_connection("default")
            self.conn.hmset(cart_key,cart_dict)
            ret["data"] = "添加成功"

        ##如果价格不合法，抛出异常
        except PriceInvalid as e:
            ret["code"] = 1006
            ret["error"] = e.msg

        #如果课程不存在，则抛出异常
        except ObjectDoesNotExist as e:
            ret["code"] = 1003
            ret["error"] = "课程不存在"
        except Exception as e:
            ret["code"] = 1003
            ret["error"] = "无法添加购物车"
        return Response(ret)

    def destory(self,request,*args,**kwargs):
        #删除购物车中课程
        print(request.data)
        ret = {"code": 1000, "data": None}
        try:
            course_id_list = request.data.get('courseids')
            key_list = [settings.SHOPPING_CART_KEY % (request.auth.user_id, course_id,) for course_id in course_id_list]
            self.conn.delete(*key_list)
            #第一种
        # course_id_list = request.data.get("courseids")
        # key_list =[]
        # for course_id in course_id_list:
        #     key = settings.SHOPPING_CART_KEY %(request.auth.user_id,course_id,)
        #     key_list.append(key)
        # self.conn.delete(*key)

        except Exception as e:
            ret['code'] = 1002
            ret['error'] = "删除失败"

        return Response(ret)

##建议用第二种，继承与APIView，URL中对应关系自带的
class ShoppingCartView(APIView):
    authentication_classes = [LuAuth,]
    conn =  get_redis_connection("default")  #下面调用要加self
    def post(self,request,*args,**kwargs):
        ret = {"code":1000,"data":None}


        try:
            print(request.data)
            #1.获取课程id和价格id要用int转化一下，数据库的id是数字，用户可能发的是字符串
            course_id = int(request.data.get("courseid"))
            price_id = int(request.data.get("priceid"))
            #2.获取专题课课程信息******
            course = models.Course.objects.get(id=course_id)
            #3.获取课程的价格策略********
            price_list = course.price_policy.all()
            print(price_list)
            price_dict = {}
            for item in price_list:
                # print(item.id)
                # print(item.valid_period)
                # print(item.get_valid_period_display())
                # print(item.price)
                price_dict[item.id]={
                    "period":item.valid_period,
                    "period_display":item.get_valid_period_display(),
                    "price":item.price
                }
            print(price_dict)
            #4.判断用户输入的价格策略是否合法
            if price_id not in price_dict:
                # ret["code"] = 2000  #第一种返回错误信息
                # ret["error"] = "价格不合法"
                raise PriceInvalid("价格不合法") #第二种自定义异常
            #5.将购物信息添加到购物车
            # cart_key = "chen_shopping_cart_%s_%s"
            print(request.auth.user_id)
            cart_key = settings.SHOPPING_CART_KEY %(request.auth.user_id,course_id,)
            print(cart_key)
            cart_dict = {
                'title':course.title,
                'img':course.course_img,
                'default_price':price_id,
                'price':json.dumps(price_dict)
            }
            print(cart_dict)
            # conn = get_redis_connection("default")
            self.conn.hmset(cart_key,cart_dict)
            ret["data"] = "添加成功"

        ##如果价格不合法，抛出异常
        except PriceInvalid as e:
            ret["code"] = 1006
            ret["error"] = e.msg

        #如果课程不存在，则抛出异常
        except ObjectDoesNotExist as e:
            ret["code"] = 1003
            ret["error"] = "课程不存在"
        except Exception as e:
            ret["code"] = 1003
            ret["error"] = "无法添加购物车"
        return Response(ret)

    def delete(self,request,*args,**kwargs):
        #删除购物车中课程
        print(request.data)
        ret = {"code": 1000, "data": None}
        try:
            course_id_list = request.data.get('courseids')
            key_list = [settings.SHOPPING_CART_KEY % (request.auth.user_id, course_id,) for course_id in course_id_list]
            self.conn.delete(*key_list)
            #第一种
        # course_id_list = request.data.get("courseids")
        # key_list =[]
        # for course_id in course_id_list:
        #     key = settings.SHOPPING_CART_KEY %(request.auth.user_id,course_id,)
        #     key_list.append(key)
        # self.conn.delete(*key)

        except Exception as e:
            ret['code'] = 1002
            ret['error'] = "删除失败"

        return Response(ret)
    def patch(self,request,*args,**kwargs):
        ret = {"code": 1000, "data": None}
        #修改课程的价格
        try:
            #1.获取价格id和课程id
            course_id = int(request.data.get("courseid"))
            price_id = str(request.data.get('priceid')) #price_dict里面是字符串，所以要改成字符串，好判断
           #2.拼接课程的key
            key = settings.SHOPPING_CART_KEY %(request.auth.user_id,course_id)
            print(course_id)
            #判断课程id是否存在
            if not self.conn.exists(key):
                ret['code'] = 1002
                ret['error'] = "课程不存在"
                return Response(ret)

            #3.判断课程价格存在不存在
            price_dict = json.loads(str(self.conn.hget(key,'price'),encoding="utf-8"))
            print("====")
            print(price_dict)
            if price_id not in price_dict:
                ret['code'] = 1002
                ret['error'] = "课程价格不存在"
                return Response(ret)

            #4.如果课程id和价格都存在，修改课程
            self.conn.hset(key,"default_price",price_id)
            ret['data'] = "修改成功"
        except Exception as e:
            ret['code'] = 1002
            ret['error'] = "修改失败"

        return Response(ret)

    def get(self,request, *args, **kwargs):
        """
        查看购物车中所有的商品
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        ret = {"code": 1000, "data": None}
        try:
            key_match = settings.SHOPPING_CART_KEY %(request.auth.user_id,"*")

            course_list = []

            for key in self.conn.scan_iter(key_match,count=10):
                price_info = {
                    "title":self.conn.hget(key,'title').decode('utf-8'),
                    "img":self.conn.hget(key,'img').decode('utf-8'),
                    "price":json.loads(self.conn.hget(key,'price').decode('utf-8')),
                    "default_price":self.conn.hget(key,'default_price').decode('utf-8')
                }
                course_list.append(price_info)
            ret["data"] = course_list
        except Exception as e:
            ret['code'] = 1002
            ret['error'] = "获取失败"
        return Response(ret)