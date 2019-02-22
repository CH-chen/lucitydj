from rest_framework.views import APIView
from rest_framework.response import Response
from lucitydj import settings
from api.auth.auth import LuAuth
from utils.reponse import BaseReponse
from django_redis import get_redis_connection
import json
from api import models
import datetime

class PayView(APIView):

    authentication_classes = [LuAuth,]
    conn = get_redis_connection("default")

    def post(self,request,*args,**kwargs):
        ret = BaseReponse()
        try:
            # 清空当前用户结算中心的数据
            # chen_payment_1_*
            # chen_payment_coupon_1
            key_list = self.conn.keys(settings.PAYMENT_KEY % (request.auth.user_id, "*",))
            key_list.append(settings.PAYMENT_COUPON_KEY % (request.auth.user_id,))
            self.conn.delete(*key_list)
            payment_dict = {}
            global_coupon_dict = {
                "coupon":{},
                "default_coupon":0
            }
            #一： 1.获取用户要结算的课程id
            print(request.data)
            course_id_list = request.data.get("courseids")



            for course_id in course_id_list:

                payment_course_dict = {}

                cart_key = settings.SHOPPING_CART_KEY %(request.auth.user_id,course_id,)
                print(cart_key)
                # 2.检测用户的课程是否加入购物车
                if not self.conn.exists(cart_key):
                    ret.code = 1002
                    ret.error = "请把课程加入购物车才能结算"

                #从购物车中获取标题和图片
                price = json.loads(self.conn.hget(cart_key,'price').decode('utf-8'))
                print(price)
                default_price = self.conn.hget(cart_key, "default_price").decode('utf-8')
                print(default_price)
                price_info = price[default_price]
                print(price_info)
                payment_course_dict = {
                    "course_id":str(course_id),
                    "title":self.conn.hget(cart_key, "title").decode("utf-8"),
                    "img":self.conn.hget(cart_key, "img").decode("utf-8"),
                    "price_id":default_price,
                    "coupon":{},
                    "default_coupon":0

                }
                print(payment_course_dict)
                payment_course_dict.update(price_info)


                payment_dict[str(course_id)] = payment_course_dict

            print(payment_dict)

            #二 获取优惠券
            # ctime = datetime.datetime.now()
            # print(ctime) #2018-10-22 20:38:32.152528
            #用这一种
            ctime = datetime.date.today()
            from django.db.models import Q
            #表达式方式
            # Q(userinfo=request.auth.user_id) & Q(status=0) | Q(coupon__valid_begin_date__lte=ctime)
            #方法
            # q = Q()
            # q1 = Q()
            # q1.connector = 'AND'
            # q1.children.append('userinfo',request.auth.user_id)
            # q1.children.append('status',0)
            # q1.children.append('coupon__valid_begin_date__lte',ctime)
            #
            # q2 = Q()
            # q2.connector = 'AND'
            # q2.children.append('coupon__valid_end_date__gte', ctime)
            #
            # q.add(q1,'OR')
            # q.add(q2,'OR')
            #
            # (userinfo = 1 and x=2) or (x=1 and xx=1)

            coupon_list = models.CouponRecord.objects.filter(
                userinfo=request.auth.user,
                status=0,
                coupon__valid_begin_date__lte=ctime,
                coupon__valid_end_date__gte=ctime,

            )
            print("======")
            print(coupon_list)
            for item in coupon_list:
                info = {}
                #只处理绑定课程的优惠券
                if not item.coupon.object_id:
                    print("这还少一个全站优惠券")
                    # 优惠券ID
                    coupon_id = item.id
                    # 优惠券类型：立减，满减，折扣
                    coupon_type = item.coupon.coupon_type
                    info["coupon_type"] = coupon_type
                    info["coupon_display"] = item.coupon.get_coupon_type_display()
                    if coupon_type == 0:  # 立减
                        info["money_equivalent_value"] = item.coupon.money_equivalent_value
                    elif coupon_type == 1:  # 满减券
                        info["money_equivalent_value"] = item.coupon.money_equivalent_value
                        info["minimum_consume"] = item.coupon.minimum_consume
                    else:  # 折扣
                        info["off_percent"] = item.coupon.off_percent

                    global_coupon_dict["coupon"][coupon_id] = info
                    continue
                #优惠券绑定课程的id
                coupon_course_id = str(item.coupon.coupon_type)
                #优惠券ID
                coupon_id = item.id
                #优惠券类型：立减，满减，折扣
                coupon_type=  item.coupon.coupon_type
                info["coupon_type"] = coupon_type
                info["coupon_display"] = item.coupon.get_coupon_type_display()
                if coupon_type == 0:#立减
                    info["money_equivalent_value"] = item.coupon.money_equivalent_value
                elif coupon_type == 1: #满减券
                    info["money_equivalent_value"] = item.coupon.money_equivalent_value
                    info["minimum_consume"] = item.coupon.minimum_consume
                else:#折扣
                    info["off_percent"] = item.coupon.off_percent

                if coupon_course_id not in payment_dict:
                    #获取到优惠券，但没有购买此课程
                    continue
                #将优惠券设置到指定课程的
                payment_dict[coupon_course_id]['coupon'][coupon_id] = info
                #可以获取绑定的优惠券
                print(payment_dict)
                print(global_coupon_dict)
                print(item.id,item.number,item.coupon.coupon_type,item.coupon.get_coupon_type_display(),item.coupon.object_id)

                # 将绑定的优惠券+全站的优惠券写到redis中
                # 1 绑定优惠券课程放入redis
                for cid, cinfo in payment_dict.items():
                    pay_key = settings.PAYMENT_KEY % (request.auth.user_id, cid,)
                    cinfo['coupon'] = json.dumps(cinfo['coupon'])
                    self.conn.hmset(pay_key, cinfo)
                # 3.2 将全站优惠券写入redis
                gcoupon_key = settings.PAYMENT_COUPON_KEY % (request.auth.user_id,)
                global_coupon_dict['coupon'] = json.dumps(global_coupon_dict['coupon'])
                self.conn.hmset(gcoupon_key, global_coupon_dict)

        except Exception as e:
            pass

        return Response(ret.dict)

    def patch(self, request, *args, **kwargs):

        ret = BaseReponse()
        try:
            # 1. 用户提交要修改的优惠券
            course = request.data.get('courseid')
            course_id = str(course) if course else course

            coupon_id = str(request.data.get('couponid'))

            # payment_global_coupon_1
            redis_global_coupon_key = settings.PAYMENT_COUPON_KEY % (request.auth.user_id,)

            # 修改全站优惠券
            if not course_id:
                if coupon_id == "0":
                    # 不使用优惠券,请求数据：{"couponid":0}
                    self.conn.hset(redis_global_coupon_key, 'default_coupon', coupon_id)
                    ret.data = "修改成功"
                    return Response(ret.dict)
                # 使用优惠券,请求数据：{"couponid":2}
                coupon_dict = json.loads(self.conn.hget(redis_global_coupon_key, 'coupon').decode('utf-8'))

                # 判断用户选择得优惠券是否合法
                if coupon_id not in coupon_dict:
                    ret.code = 1001
                    ret.error = "全站优惠券不存在"
                    return Response(ret.dict)

                # 选择的优惠券合法
                self.conn.hset(redis_global_coupon_key, 'default_coupon', coupon_id)
                ret.data = "修改成功"
                return Response(ret.dict)

            # 修改课程优惠券
            # chen_payment_1_1
            redis_payment_key = settings.PAYMENT_KEY % (request.auth.user_id, course_id,)
            # 不使用优惠券
            if coupon_id == "0":
                self.conn.hset(redis_payment_key, 'default_coupon', coupon_id)
                ret.data = "修改成功"
                return Response(ret.dict)

            # 使用优惠券
            coupon_dict = json.loads(self.conn.hget(redis_payment_key, 'coupon').decode('utf-8'))
            if coupon_id not in coupon_dict:
                ret.code = 1010
                ret.error = "课程优惠券不存在"
                return Response(ret.dict)

            self.conn.hset(redis_payment_key, 'default_coupon', coupon_id)

        except Exception as e:
            ret.code = 1111
            ret.error = "修改失败"

        return Response(ret.dict)

    def get(self, request, *args, **kwargs):

        ret = BaseReponse()

        try:
            # chen_payment_1_*
            redis_payment_key = settings.PAYMENT_KEY % (request.auth.user_id, "*",)

            # chen_payment_coupon_1
            redis_global_coupon_key = settings.PAYMENT_COUPON_KEY % (request.auth.user_id,)

            # 1. 获取绑定课程信息
            course_list = []
            for key in self.conn.scan_iter(redis_payment_key):
                info = {}
                data = self.conn.hgetall(key)
                for k, v in data.items():
                    kk = k.decode('utf-8')
                    if kk == "coupon":
                        info[kk] = json.loads(v.decode('utf-8'))
                    else:
                        info[kk] = v.decode('utf-8')
                course_list.append(info)

            # 2.全站优惠券
            global_coupon_dict = {
                'coupon': json.loads(self.conn.hget(redis_global_coupon_key, 'coupon').decode('utf-8')),
                'default_coupon': self.conn.hget(redis_global_coupon_key, 'default_coupon').decode('utf-8')
            }

            ret.data = {
                "course_list": course_list,
                "global_coupon_dict": global_coupon_dict
            }
        except Exception as e:
            ret.code = 1001
            ret.error = "获取失败"

        return Response(ret.dict)



