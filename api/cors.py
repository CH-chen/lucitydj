from django.middleware.common import MiddlewareMixin

class CORSMiddleware(MiddlewareMixin):
    def process_response(self,request,response):
        #添加响应头
        # response['aaa'] = 6666
        # #允许你的域名来获取我的数据
        # response['Access-Control-Allow-Origin'] = '*'
        # #允许携带请求头Content-Type
        # response['Access-Control-Allow-Headers'] = 'Content-Type,xxxx,88888'
        # #允许发送DELETE,PUT
        # response['Access-Control-Allow-Methods'] = 'DELETE,PUT'
        response['Access-Control-Allow-Origin'] = '*'

        if request.method == "OPTIONS":
            response['Access-Control-Allow-Headers'] = "Content-Type"
            response['Access-Control-Allow-Methods'] = "PUT,DELETE"
        return response
