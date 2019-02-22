from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api import models

class LuAuth(BaseAuthentication):
    def authenticate(self,request):
        token = request.query_params.get('token')
        obj = models.UserToken.objects.filter(token=token).first()
        if not obj:
            raise AuthenticationFailed({'code':1001,'error':'认证失败'})

        return (obj.user.username,obj)   #obj.user.username返回对应的ruquest.user, obj返回对应的request.auth