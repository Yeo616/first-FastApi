# 2022.11.29
# MongoDB 로컬/ URL로 Connect 및 파이썬에서 접근 test
# 데이터 insert, 

# from pymongo import MongoClient
# import datetime
# import pprint 

# # print(pymongo.__version__)

# # 기본 호스트와 포트에 연결

# # mongodb_URI= "mongodb+srv://admin2:123456789a@cluster0.loapi14.mongodb.net/?retryWrites=true&w=majority"
# client = MongoClient()

# print("01. " + str(client)) # 잘 연결되었는 지 확인. 
# # print(client.list_database_names()) -> 얘 안됨

# # 데이터베이스 
# # db = client.test_database
# db = client['test']

# print("02. " + str(db))

# # # 컬렉션
# # collection = db.test_collection
# collection = db['users']

# print("03. " + str(collection))


# # 문서
# post = {"author": "Mike",
#         "text": "My Ffirst blog post!",
#         "tags": ["mongodb",'python','pymongo'],
#         "date": datetime.datetime.utcnow()
# }

# print("04. ")
# print(post)

# #Collection 접근 - 'posts Collection
# users = db.users

# print("05. ")
# print(users)

# # Document 입력: insert_one()
# users.insert_one(post)

# # -id 값을 추가할 때 키가 없으면 특수 키가 자동으로 추가된다. "-id"의 값은 고유 값.
# #ObjectId로 포스트를 찾을 수 있다. 

# # 단일 값 찾아내기 : find_one()
# print("09. ")
# pprint.pprint(users.find_one(users.find_one()))
# pprint.pprint(users.find_one({"author":"Mike"}))

# # 다량의 내용 삽입
# new_posts = [{"author":"Mike",
#             "text":"Author posts!",
#             "tags":["bulk","inserts"],
#             "date": datetime.datetime.utcnow()},

#             {"author":"Eliot",
#             "text":"MongoDB is fun!",
#             "tags":"and pretty easy too!",
#             "date": datetime.datetime(2009,11,10,10,45)}
# ]

# result = users.insert_many(new_posts)

# print("10. ")
# print(result)
# print(result.inserted_ids)

# # 여러 Documents 조회: find()
# for post in users.find():
#     pprint.pprint(post)


# # 쿼리를 통한 Documents 조회
# for post in users.find({"author": "Mike"}):
#     pprint.pprint(post)

# ##  카운팅
# # 컬렉션 내 Document 수 조회
# users.count_documents({})

# # 쿼리를 통한 도큐먼트 수 조회
# users.count_documents({"author":"Mike"})

# ## 범위 쿼리

# d = datetime.datetime(2022, 11, 29, 12)

# for post in users.find({"date": {"$lt": d}}).sort("author"):
#     pprint.pprint(post)


# ## 인덱싱
# # import pymongo

# result = db.users.create_index([('user_id', pymongo.ASCENDING)],unique=True)


# # 두 개의 인덱스 확인
# sorted(list(db.users.index_information()))

# # 유저 정보 관련 document 생성
# user_profiles = [
    
#     {"user_id": 211, "name": "Luke"},
#     {"user_id": 212, "name": "Ziltoid"}
    
# ]

# # documents 추가
# result = db.users.insert_many(user_profiles)

# # 이미 컬렉션에 있는 user_id이면 추가 방지
# new_profile = {"user_id": 213, "name": "Drew"}
# duplicate_profile = {"user_id": 212, "name": "Tommy"}

# # user_id 신규 이므로 정상 추가 됨
# result = db.users.insert_one(new_profile)

# try:
#     # user_id 기존에 있으므로 추가 안 됨
#     result = db.users.insert_one(duplicate_profile)
# except:
#     print("Error")

# for doc in db.profiles.find():
#     pprint.pprint(doc)

# # 로그인시 필요한 DB 준비

from pymongo import MongoClient, InsertOne, DeleteOne, ReplaceOne
import datetime

# MongoDB 클라이언트 인스턴스 생성
# mongodb_URI= "mongodb+srv://admin2:123456789a@cluster0.loapi14.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient()

# 테스트 DB 정의
db = client.test

# 데이터 리스트 정의
data = [{
     "email": "test8@naver.com", 
     "password":"123456789(needed to be hased)",
     "nickname": "8",
     "status":"junior",
     "region":"",
     "username":"",
     "phone_number":"",
     "profile_pic":"",
     "shopping_cart":{
         "program":{
             "program_title":"test",
             "courses":{
                 "course_title":"test",
                 "price":1,
                 "student_amount":10 },
             "start_date": "2022-11-29",
             "end_date": "2023-11-29"
         }
     },
     "reservation":{
        "program":{
             "program_title":"test2",
             "courses":{
                 "course_title":"test2",
                 "price":2,
                 "student_amount":20
             },
             "start_date": "2022-11-29",
             "end_date": "2023-11-29"
         },
         "payment": "TRUE"
     },
     "created_at":datetime.datetime.utcnow(),
     "comment":""
    },
    {
     "email": "test9@naver.com(created_time modified)", 
     "password":"123456789(needed to be hased)",
     "nickname": "9",
     "status":"junior",
     "region":"",
     "username":"",
     "phone_number":"",
     "profile_pic":"",
     "shopping_cart":{
         "program":{
             "program_title":"test",
             "courses":{
                 "course_title":"test",
                 "price":1,
                 "student_amount":10 },
             "start_date": "2022-11-29",
             "end_date": "2023-11-29"
         }
     },
     "reservation":{
        "program":{
             "program_title":"test2",
             "courses":{
                 "course_title":"test2",
                 "price":2,
                 "student_amount":20
             },
             "start_date": "2022-11-29",
             "end_date": "2023-11-29"
         },
         "payment": "TRUE"
     },
     "created_at":datetime.datetime.utcnow(),
     "comment":""
    }]

# things 컬렉션에 데이터 벌크 인서트 수행
result = db.users.insert_many(data)

# 추가된 Documents의 ID 확인
result.inserted_ids

## Field Updatd

updated_result = db.users.update_many({'email':'test8@naver.com(created_time modified)'},{'$set':{'nickname': '8'}})

# 참고 : https://www.w3schools.com/python/python_mongodb_update.asp

# update이후의 collection 확인

for x in db.users.find():
  print(x)

## Delete Field

myquery = {'email': {'$regex':'^a'}}
x = db.users.delete_many(myquery)

print(x.deleted_count," documents deleted")

for x in db.users.find():
  print(x)

## Delete Field -One

myquery = {'_id': '6385be9418bf9dfaab11b279'}
x = db.users.delete_one(myquery)

print(x.deleted_count," documents deleted")

for x in db.users.find():
  print(x)

## Sort

mydoc = db.users.find().sort("nickname")

for x in mydoc:
  print(x)

## Drop Collection

db.posts.drop()



