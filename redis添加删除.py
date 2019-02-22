import redis
import json
conn = redis.Redis(host='192.168.170.138',port=6379,password='chenchen')
# #
conn.flushall()

#添加课程
redis_key = "chen_shopping_car_%s_%s" %(9,18,)
conn.hmset(redis_key,{'title':'python基础','src':'111.png'})
print(conn.hgetall(redis_key))  #{b'title': b'python\xe5\x9f\xba\xe7\xa1\x80', b'src': b'111.png'}

print(conn.keys())  #[b'chen_shopping_car_9_18']
# #删除课程
# conn.delete('chen_shopping_car_9_18')
# print(conn.keys())  #[]

#修改课程

conn.hset('chen_shopping_car_9_18','src','666.png')
print(conn.keys())
print(conn.hget('chen_shopping_car_9_18','src'))    #b'666.png
#
conn.hset('chen_shopping_car_9_19','src','999.png')
# #查看所有课程
print(conn.keys('chen_shopping_car_9_*'))   #[b'chen_shopping_car_9_19', b'chen_shopping_car_9_18']

for item in conn.scan_iter('chen_shopping_car_9_*',count=10):
    print(item) #b'chen_shopping_car_9_19'  'chen_shopping_car_9_18'
    course = conn.hgetall(item)
    print(course)   #{b'src': b'999.png'}   b'title': b'python\xe5\x9f\xba\xe7\xa1\x80', b'src': b'666.png'}

# conn.flushall()
# print(conn.keys())
# for key in conn.scan_iter('chen_shopping_cart_2_1'):
#     title = conn.hget(key, 'title')
#     img = conn.hget(key, 'img')
#     price = conn.hget(key, 'price')
#     conn.hget(key, 'default_price')
#
#     print(str(title, "utf-8"))
#     print(str(img, "utf-8"))
#     print(json.loads(str(price, "utf-8")))
#     print(str(key, "utf-8"))
#
# print(conn.exists('chen_shopping_cart_2_1'))
# conn.hgetall('chen_shopping_cart_2_3')
# title = conn.hget('chen_shopping_cart_2_3','title')
# print(str(title,"utf-8"))
# img = conn.hget('chen_shopping_cart_2_3','img')
# print(str(img,"utf-8"))
# # print(conn.hget('chen_shopping_cart_2_3','price'))
# price = conn.hget('chen_shopping_cart_2_3','price') #字典
# print(json.loads(str(price,"utf-8")))
# default_price = conn.hget('chen_shopping_cart_2_3','default_price')
# print(str(default_price,"utf-8"))