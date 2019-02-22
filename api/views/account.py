from rest_framework.views import APIView
from rest_framework.response import Response
from api import models
from utils.reponse import BaseReponse
import uuid

class AuthorView(APIView):
    #如果为put,delete等特殊请求cors要添加
    # def PUT(self,request,*args,**kwargs):
    #     print(request.data)
    #     return Response('======')

    #第一种
    def post(self,request,*args,**kwargs):
        # 用户登录认证
        print(request.data)
        # ret = {'code':1000}  #第一种以字典形式
        ret = BaseReponse()  #第二种 封装响应对象
        # username = request.data['username'] //也可以这样写，如果不存在则容易报错
        try:
            username = request.data.get('user')
            password = request.data.get('pwd')
            user = models.UserInfo.objects.filter(username=username,password=password).first()
            if not user:
                # ret['code'] = 1001  #第一种以字典形式
                # ret['error'] = '用户名或密码错误' #第一种以字典形式
                ret.code = 1000
                ret.error="用户名或者密码错误"
            else:
                uid = str(uuid.uuid4())
                print(uid)
                models.UserToken.objects.update_or_create(user=user,defaults={'token':uid})
                # ret['token'] = uid  #第一种以字典形式
                ret.data = uid
        except Exception as e:
            # ret['code'] = 1004 #第一种以字典形式
            ret.code = 1004
        #如果数据哭出问题无法连接到，要捕获# 异常，所以用try,except
        return Response(ret.dict)

    # 第二种
    # def post(self,request,*args,**kwargs):
    #     # 用户登录认证
    #     print(request.data)
    #     ret = {'code':1000}
    #     # username = request.data['username'] //也可以这样写，如果不存在则容易报错
    #     try:
    #         username = request.data.get('user')
    #         password = request.data.get('pwd')
    #         user = models.UserInfo.objects.filter(username=username,password=password).first()
    #         if not user:
    #             ret['code'] = 1001
    #             ret['error'] = '用户名或密码错误'
    #
    #         uid = str(uuid.uuid4())
    #         print(uid)
    #         models.UserToken.objects.update_or_create(user=user,defaults={'token':uid})
    #         ret['token'] = uid
    #     except Exception as e:
    #         ret['code'] = 1004
    #     #如果数据哭出问题无法连接到，要捕获异常，所以用try,except
    #     return Response(ret)