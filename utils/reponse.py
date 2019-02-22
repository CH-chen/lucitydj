class BaseReponse(object):
    def __init__(self):
        self.code = 1000
        self.data = None
        self.error = None
    @property
    def dict(self):
        return self.__dict__

# ret = BaseReponse()
# print(ret)
# print(ret.code)
# print(ret.dict)
# print(ret.__dict__)  #打印内容：{'code': 1000, 'data': None, 'error': None}