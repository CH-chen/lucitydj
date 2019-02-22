from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet,ViewSetMixin,ModelViewSet,mixins
from rest_framework import serializers
from api import models
from api.auth.auth import LuAuth

# Create your views here.

class CourseModelSerializer(serializers.ModelSerializer):
     #第一种 level显示数字
    # class Meta:
    #     model = models.Course
    #     fields = "__all__"
    #第二种level显示汉字
    level = serializers.CharField(source='get_level_display')
    class Meta:
        model = models.Course
        fields = ['id','title','course_img','level']

# class CourseDetailModelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.CourseDetail
#         fields = "__all__"
#         depth = 2 #0-10所有关联字段显示
#自定义字段
class CourseDetailModelSerializer(serializers.ModelSerializer):
    '''source在onetoone,foreignkey,choice这些使用，多对多不适用'''''
    #显示course表中的字段
    title = serializers.CharField(source='course.title')
    image = serializers.CharField(source='course.course_img')
    level = serializers.CharField(source='course.level')
    level_hz = serializers.CharField(source='course.get_level_display')#显示choice中的汉字而不是数字
    '''多对多的使用'''
    recommend = serializers.SerializerMethodField()
    chapers = serializers.SerializerMethodField()
    class Meta:
        model = models.CourseDetail
        fields = ['title','why','slogon','image','course_id','level','level_hz','course','course_recommend','recommend','chapers'] #自定义指定的关联显示字段
        depth = 2 #0-10所有关联字段显示
    def get_recommend(self,obj):
        queryset = obj.course_recommend.all()
        return [{'id':item.id,'title':item.title}for item in queryset]
    def get_chapers(self,obj):
        print(obj)
        queryset = obj.course.chapers_set.all()
        return [{'id':item.id,'title':item.name}for item in queryset]

class Chapers(serializers.ModelSerializer):
    class Meta:
        model = models.Chapers
        fields = "__all__"

########深科技##########

class ArticleSourceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ArticleSource
        fields = "__all__"

class ArticleModelSerializers(serializers.ModelSerializer):
    source = serializers.CharField(source="source.name")
    article_type = serializers.CharField(source="get_article_type_display")
    position = serializers.CharField(source='get_position_display')

    class Meta:
        model = models.Article
        fields = ["title", "source", "article_type", 'head_img', 'brief', 'pub_date', 'comment_num', 'agree_num',
                  'view_num', 'collect_num', 'position']


class ArticleDetailModelSerializers(serializers.ModelSerializer):
    class Meta:
        model = models.Article
        fields = ['title', 'pub_date', 'agree_num', 'view_num', 'collect_num', 'comment_num', 'source', 'content',
                  'head_img']


class CollectionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = "__all__"

class CommentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = "__all__"


# class CourseView1(APIView):
#     def get(self,request,*args,**kwargs):
#         ret = {
#             'code':1000,
#             'data':[
#                 {'id':1,'title':'python'},
#                 {'id':2,'title':'django'},
#                 {'id':3,'title':'vue'},
#                 {'id':4,'title':'web'},
#             ]
#         }
#         return Response(ret)
#第一种
# class CourseView(APIView):
#     def get(self,request,*args,**kwargs):
#         ret = {'code':1000,'data':None}
#         try:
#             pk = kwargs.get('pk')
#             if pk:
#                 obj = models.Course.objects.filter(id=pk).first()
#                 ser = CourseModelSerializer(instance=obj,many=False)
#             else:
#                 list = models.Course.objects.all()
#                 ser = CourseModelSerializer(instance=list,many=True)
#             ret['data'] = ser.data
#         except Exception as e:
#             ret['code'] =1001
#             ret['data'] ='无法获取数据'
#
#         return Response(ret)

# 第二种 继承ViewSetMixin,APIView
from rest_framework.viewsets import GenericViewSet,ViewSetMixin
class CourseView(ViewSetMixin,APIView):

    def list(self,request,*args,**kwargs):
        print(request.version)

        ret = {'code': 1000, 'data': None}
        try:
            list = models.Course.objects.all()
            ser = CourseModelSerializer(instance=list, many=True)
            ret['data'] = ser.data
        except Exception as e:
            ret['code'] = 1001
            ret['data'] = '无法获取数据'
        return Response(ret)


    def retrieve(self,request,*args,**kwargs):

        ret = {'code': 1000, 'data': None}
        # try:
        #     pk = kwargs.get('pk')
        #     obj = models.Course.objects.filter(id=pk).first()
        #     ser = CourseModelSerializer(instance=obj, many=False)
        #     ret['data'] = ser.data
        try:
            pk = kwargs.get('pk')
            obj = models.CourseDetail.objects.filter(course_id=pk).first()
            ser = CourseDetailModelSerializer(instance=obj, many=False)
            ret['data'] = ser.data
        except Exception as e:
            ret['code'] = 1002
            ret['data'] ='无法获取数据'
        return Response(ret)

#第三种这个是简单请求，可以直接这样写，继承mixins,GenericViewSet
# class CourseView(mixins.ListModelMixin,mixins.RetrieveModelMixin,GenericViewSet):
#     queryset = models.Course.objects.all()
#     serializer_class = CourseModelSerializer




class ArticleView(ViewSetMixin,APIView): #ViewSetMixin,APIView这两个前后不能换，会报错

    def list(self, request, *args, **kwargs):

        ret = {'code': 1000, 'data': None}
        try:
            list = models.Article.objects.all()
            ser = ArticleModelSerializers(instance=list, many=True)
            ret['data'] = ser.data
        except Exception as e:
            ret['code'] = 1001
            ret['data'] = '无法获取数据'
        return Response(ret)

    def retrieve(self,request,*args,**kwargs):
        ret = {'code': 1000, 'data': None}

        try:
            pk = kwargs.get('pk')
            obj = models.Article.objects.filter(pk=pk).first()
            # ser = ArticleModelSerializers(instance=obj, many=False)#可以写成一个，也可以写成两个
            ser = ArticleDetailModelSerializers(instance=obj,many=False)
            ret['data'] = ser.data
        except Exception as e:
            ret['code'] = 1003
            ret['data'] = '无法获取数据'
        return Response(ret)


class AgreeView(ViewSetMixin,APIView):
    def post(self,request,*args,**kwargs):

        ret = {'code':1000,'data':None}
        try:
            pk = kwargs.get('pk')
            # 更新赞数，方式一
            obj = models.Article.objects.filter(pk=pk).first()
            obj.agree_num = obj.agree_num + 1
            obj.save()
            #方式二
            #F,更新数据库字段
            #Q，构造复杂条件
            # from django.db.models import F,Q
            # num = models.Article.objects.filter(pk=pk).update(agree_num=F("agree_num") + 1)
            # print(num)
            # print("===========")
            # ret['data'] = num

            ret['data'] = obj.agree_num
        except Exception as e:
            ret['code'] = 1003
            ret['data'] = '无法点赞'
        return Response(ret)









class CenterView(APIView):
    authentication_classes = [LuAuth,]
    def get(self,request,*args,**kwargs):
        print(request.user)
        print(request.auth)
        ret={'code':1000,'title':'姓名工作地址'}
        return Response(ret)