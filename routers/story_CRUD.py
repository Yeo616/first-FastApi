# from fastapi import APIRouter, HTTPException, Header, Query, File, UploadFile
# from fastapi.security import OAuth2PasswordBearer
# from pydantic import  BaseModel
# # from pyjwt import decode, InvalidTokenError
# from datetime import datetime
# from fastapi.security import OAuth2PasswordBearer
# # from jose import JWTError, jwt
# import jwt

# router = APIRouter(prefix='/story')

# # UPLOAD_DIRECTORY = "./saving_images/"

# class StoryPost(BaseModel): # 스키마 모델링
#     program_title : str # essential, 연관된 프로그램 제목
#     # program_id : str # essential, 연관된 프로그램 제목 DB 저장된 id

#     title:str # essential, 스토리 제목
#     content:str # essential, 스토리 내용
#     degree: str # essential, 회원 등급
#     on_offline: str # essential, 수업 방식
#     class_contents: str # essential, 수업 내용
#     advance : str # essential, 기존 조건

#     # img: str | None = None # non-essential, 스토리 내용 삽입 이미지

#     author: str # essential, 작성자 email

#     created_at: datetime = datetime.now() # essential, 스토리 생성 날짜
#     updated_at: datetime| None = None # non-essential, 스토리 수정 날짜

#     class config:
#         schema_extra = {
#         "program_title": "test1",
#         "title":"title",
#         "content":"write from here",
#         "degree": "nobase",
#         "on_offline": "online",
#         "class_contents": "reading",
#         "advance" : "quality",
#         "author": "your email",
#         "created_at" : datetime.now()}

# class Degree(str): ## 회원 등급
#     nobase: str = "nobase" 
#     elementry: str = "elementry"
#     middle: str = "middle"
#     high: str = "high"
#     university: str = "university"

# class on_offline(str): ## 수업 방식
#     online: str = "online"
#     offline: str = "offline"
#     on_offline: str = "on_offline"
#     visit: str = "visit"
#     outisde: str = "outisde"

# class Class_contents(str): ## 수업 내용
#     phonics: str = "phonics"
#     reading: str = "reading"
#     toeic_ielts: str = "toeic_ielts"
#     business_english: str = "business_english"
#     job_interview: str = "job_interview"
#     etc: str = "etc"

# class Advance(str): ## 기존 조건
#     quality:str = "quality"
#     facilities:str = "facilities"
#     price : str = "price"
#     enviornment : str = "enviornment"
#     system : str = "system"

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')

# JWT_SECRET = 'adcec27a3417b2de82130a2c54fc5c65aca0d7fa41b0a01dc310f3c78a62f885'
# JWT_ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# import math

# # 선택으로 검색기능, (토큰x, 페이징 처리)
# @router.get("/search_option", tags=["story_without_Token"])
# async def search_programs(
#                         search_option_degree:Degree = None, 
#                         search_option_on_offline:on_offline = None,
#                         search_option_class_contents:Class_contents = None,
#                         search_option_class_advance:Advance = None,
#                         page: int = Query(1, description="Page number", ge=1)
#                         ):

#     print("first 2 datas : ", search_option_degree, search_option_on_offline)
#     print("last 2 datas : ", search_option_class_contents, search_option_class_advance)

#     # 페이징: 한 페이지 당 몇 개의 게시물을 출력할 것인가
#     limit = 3
 
#     # DB연결
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     db = myclient["test"]["story_db"]
#     print("db is connected.")

#     # 입력값이 없을 경우: 모든 데이터 출력
#     if search_option_degree is None and search_option_on_offline is None and search_option_class_contents is None and search_option_class_advance is None:
        
#         # datas = db.find({}) # 페이징 처리 안할 때
#         datas = db.find({}).skip((page - 1) * limit).limit(limit) # 페이징 처리
#         print("no input data, return all the data")
#         datas = list(datas)
#         print(datas)
#         return datas  # program_db 컬럭션에 있는 모든 데이터를 가져옴

#     option_list = [search_option_degree, search_option_on_offline, search_option_class_contents, search_option_class_advance]
     
#     # None값이 아닌 것 걸러내기
#     search_option_list = []
#     for i in option_list:
#         if i is not None:
#             search_option_list.append(i)
#             print(f"{i} has appended to search_option_list")
    
#     # None값이 아닌 것 중에 판단하기 
#     query_list= []
#     for i in search_option_list:       
#         if i == search_option_degree:
#             result_1 = {"degree":search_option_degree}
#             query_list.append(result_1)
#             print("result_1 has appended to query_list.")

#         if i == search_option_on_offline:
#             result_2 = {"on_offline":search_option_on_offline}
#             query_list.append(result_2)
#             print("result_2 has appended to query_list.")

#         if i == search_option_class_contents:
#             result_3 = {"class_contents":search_option_class_contents}
#             query_list.append(result_3)
#             print("result_3 has appended to query_list.")

#         if i == search_option_class_advance:
#             result_4 = {"advance":search_option_class_advance}
#             query_list.append(result_4)
#             print("result_4 has appended to query_list.")
      

#     if len(query_list)>=2:
#         query = {"$and" : query_list} 
#         print(f"{len(query_list)} query was created.")

#     else:
#         query = query_list[0]
#         print("1 query was created.")
        
#     # Issue the query to the "documents" collection
#     # 검색 결과에서 가져올 데이터만 추린다. 
#     results = db.find(query)
#     results = list(results)
#     print("results: ", results)
#     print(f"results: {len(results)} results were returned.")

#     # 결과값이 없으면
#     if len(results) <= 0:
#         return {"results": "No data found"}
    

#     # limit(한 페이지에 보여주는 결과) 보다 결과값이 적으면, 페이징 처리할 필요가 없음
#     if len(results) <= limit:
#         return results
#     else:
#         results = db.find(query).skip((page - 1) * limit).limit(limit)

#     # limit보다 결과물이 많을 때
#     # 페이징: 게시물의 총 개수 세기
#     tot_count = len(list(db.find(query)))
#     print("tot_count: ", tot_count)

#     # 페이징: 마지막 페이지의 수 구하기
#     last_page_num = math.ceil(tot_count / limit) # 페이징: 반드시 올림을 해줘야함
#     print("last_page_num: ", last_page_num)

#     if last_page_num < page:    # 페이징: 페이지 번호가 마지막 페이지 수보다 클때 에러 발생
#         raise HTTPException(
#                     status_code = 400,detail=f'last pagination is {last_page_num}, page number shoule be less than last page number')

#     # 페이징: 페이지 블럭을 5개씩 표기
#     block_size = 5

#     # 페이징: 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
#     block_num = int((page - 1) / block_size)
#     print("block_num: ", block_num)

#     # 페이징: 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
#     block_start = (block_size * block_num) + 1
#     print("block_start: ", block_start)

#     # 페이징: 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
#     block_end = block_start + (block_size - 1)
#     print("block_end: ", block_end)
   
#     return results

# def validate_token(token: str):
#     try:
#         decoded_info = jwt.decode(f'Bearer {token}', JWT_SECRET , [JWT_ALGORITHM])
#         print(decoded_info['sub'])
#         return decoded_info
#     except:
#         raise HTTPException(status_code=401, detail= 'Invalid token')


# import pymongo
# from bson import json_util
# from bson.objectid import ObjectId

# from fastapi.responses import FileResponse
# import os
# from typing import List
# import uuid

# # 토큰없이 테스트
# @router.post("/posts/test", tags=['story_without_Token'])
# async def create_post_test(post: StoryPost,
#                            files: UploadFile = File(default=None)
#                      ):

#     print("had input : ",post )
#     # print("files : ",files)

#     # 사전 유효성 검사
#     degree_list = ["nobase", "elementary", "middle", "high", "university"]
#     on_offline_list = ["online", "offline", "on_offline", "visit", "outside"]
#     class_contents_list = ["phonics", "reading", "toeic_ielts", "business_english", "job_interview", "etc"]
#     advance_list = ["quality", "facilities", "price", "environment", "system"]

#     if not post.degree in degree_list:
#         raise HTTPException(status_code=400, detail="wrong degree input") 
   
#     if not post.on_offline in on_offline_list:
#         raise HTTPException(status_code=400, detail="wrong on_offline input") 
   
#     if not post.class_contents in class_contents_list:
#         raise HTTPException(status_code=400, detail="wrong class_contents input") 

#     if not post.advance in advance_list:
#         raise HTTPException(status_code=400, detail="wrong advance input") 

#     # DB연결
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
   
#     #프로그램 관련 DB 연결
#     program_db = myclient['test']['program_db']
#     program_title = post.program_title
#     # 입력받은 값: program_title
#     program_info_db = program_db.find({"program_title": program_title})
#     program_info_db = list(program_info_db)
#     print("program_title_db : ", program_info_db)
#     print("len(program_title_db) : ", len(program_info_db))

#     # program_title 입력이 잘못 되었을 경우
#     if len(program_info_db) != 1:
#         raise HTTPException(status_code=400, detail="wrong program title") 
#     print("program_title_count : ",program_db.count_documents({"program_title": post.program_title}))

#     # 참고하는 프로그램 정보
#     program_id = program_info_db[0]['_id']
#     print("program_title_db_id : ", program_id)

#     # DB연결
#     db = myclient["test"]["story_db"]
    
#     data = {"program_title": post.program_title,
#             "program_id": program_id,
#             "title": post.title, 
#             "content":post.content, 
#             "degree": post.degree,
#             "on_offline": post.on_offline,
#             "class_contents": post.class_contents,
#             "advance" : post.advance,
#             "author": "test",
#             "created_at": datetime.now()}

#     content = db.insert_one(data)
#     # print("content : ", content)
#     content_id = content.inserted_id
#     print("this content_id : ",content_id)

#     # 생성한 content_id
#     data_in_db = db.find_one({"_id": ObjectId(content_id)})
#     print("content : ", data_in_db)
    
#     if files is None:
#         return {"content_id":f"{content_id}", # 스토리 콘텐츠 아이디
#                 "content_data": data_in_db,   # 스토리 입력 값
#                 "program_info":f"{program_info_db}"} # 연관된 프로그램 정보
    
#     ##============ 이미지 업로드(대표 이미지) ==================
    
#     # 이미지 저장할 경로 지정
#     UPLOAD_DIRECTORY = "./saving_images/"
#     LOCAL_URL = "http://localhost:8000"

#     path_list = []

#     # 이미지 DB 연결
#     image_db = myclient["test"]["image_db"]

#     currentTime = datetime.now().strftime("%Y%m%d%H%M%S")
#     for file in files:
#         contents = await file.read() # 파일을 읽는 동안 CPU가 다른 일을 하도록 명령
#         saved_file_name = f"{currentTime}{str(uuid.uuid4())}.jpg" # 업로드한 시간과 UUID를 이용해서 유니크한 파일명으로 변경
#         saved_file_path = f"{LOCAL_URL}/images/{saved_file_name}" # localhost:8000/ 파일 경로 url

#         # DB에 이미지 저장
#         image_data = {"image_url": saved_file_path,
#                   "image_name": saved_file_name,
#                   "story_refered_id": program_id,
#                   "created_at": datetime.now()}

#         image_content = image_db.insert_one(image_data)
#         image_content_id = image_content.inserted_id
#         print("image content_id : ",image_content_id)

#         print("original file name: ",file.filename)
#         print("file_names : ",saved_file_name)
#         print("file_path: ",saved_file_path)

#         with open(os.path.join(UPLOAD_DIRECTORY, saved_file_name), "wb") as fp: # 해당 경로에 있는 파일을 바이러니 형식으로 open
#             fp.write(contents) # 로컬에 이미지 저장(쓰기)
#             path_list.append(saved_file_path)
    
#     # 연관된 프로그램 정보도 넘기게 하였음.
#     # return {"file_path": [saved_file_path for file in files], } # 파일 더미에서 각 저장한 경로 및 파일명 호출
#     return {"file_path": [file for file in path_list], # 파일 더미에서 각 저장한 경로 및 파일명 호출
#             "content_id":f"{content_id}", # 스토리 콘텐츠 아이디
#             "content_data": data_in_db,   # 스토리 입력 값
#             "program_info":f"{program_info_db}"} # 연관된 프로그램 정보

# # create a new story post with token
# @router.post("/posts", tags=['story'])
# def create_post(post: StoryPost, token: str = Header()):
#     try :
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
#     except:
#         raise HTTPException(status_code=401, detail='Invaild token')

#     print("payload : ",payload)

#     if 'email' in payload:
#         author = payload['email']
#     else:
#         author = payload['sub']

#     # 사전 유효성 검사
#     degree_list = ["nobase", "elementary", "middle", "high", "university"]
#     on_offline_list = ["online", "offline", "on_offline", "visit", "outside"]
#     class_contents_list = ["phonics", "reading", "toeic_ielts", "business_english", "job_interview", "etc"]
#     advance_list = ["quality", "facilities", "price", "environment", "system"]

#     if not post.degree in degree_list:
#         raise HTTPException(status_code=400, detail="wrong degree input")
   
#     if not post.on_offline in on_offline_list:
#         raise HTTPException(status_code=400, detail="wrong on_offline input")
   
#     if not post.class_contents in class_contents_list:
#         raise HTTPException(status_code=400, detail="wrong class_contents input")

#     if not post.advance in advance_list:
#         raise HTTPException(status_code=400, detail="wrong advance input")

#     # DB연결
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
   
#     #프로그램 관련 DB 연결
#     program_db = myclient['test']['program_db']
#     program_title = post.program_title
#     # 입력받은 값: program_title
#     program_info_db = program_db.find({"program_title": program_title})
#     program_info_db = list(program_info_db)
#     print("program_title_db : ", program_info_db)
#     print("len(program_title_db) : ", len(program_info_db))

#     # program_title 입력이 잘못 되었을 경우
#     if len(program_info_db) != 1:
#         raise HTTPException(status_code=400, detail="wrong program title")
#     print("program_title_count : ",program_db.count_documents({"program_title": post.program_title}))

#     # 참고하는 프로그램 정보
#     program_id = program_info_db[0]['_id']
#     print("program_title_db_id : ", program_id)

#     # DB연결
#     db = myclient["test"]["story_db"]
   
#     data = {"program_title": post.program_title,
#             "program_id": program_id,
#             "title": post.title,
#             "content":post.content,
#             "degree": post.degree,
#             "on_offline": post.on_offline,
#             "class_contents": post.class_contents,
#             "advance" : post.advance,
#             "author": author,
#             "created_at": datetime.now()}

#     content = db.insert_one(data)
#     # print("content : ", content)
#     content_id = content.inserted_id
#     print("this content_id : ",content_id)

#     # 생성한 content_id
#     data_in_db = db.find_one({"_id": ObjectId(content_id)})
#     print("content : ", data_in_db)
   

#     return {"content_id":f"{content_id}", # 스토리 콘텐츠 아이디
#             "content_data": data_in_db,   # 스토리 입력 값
#             "program_info":f"{program_info_db}"} # 연관된 프로그램 정보

# import json
# from typing import List
# import pydantic
# pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

# # read all story posts with token (whitch all author wrote)
# @router.get("/posts/token", tags=['story']) 
# def read_all_posts( token: str = Header(), skip: int = 0, limit: int = 10,):  
#     try :
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
#     except:
#         raise HTTPException(status_code=401, detail='Invaild token')

#     print("payload : ",payload)

#     if 'email' in payload:
#         author = payload['email']
#     else:
#         author = payload['sub']
    
#     # DB연결
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     db = myclient["test"]["story_db"]

#     # TODO: decoded token and the author info are needed
#     # content = db.find({},{"author": "decoded token"})
#     content = db.find({"author": author})

#     return_list = []
#     j=0
#     for i in content:
#         return_list.append(i)
#         j+=1
#         print(f"content{j}: ", i)

#     print("List : ",return_list)
#     json_list = json.loads(json_util.dumps(return_list))
#     print("List in Json : ", json_list)
#     return json_list

# # # read all story posts without token
# # @router.get("/posts", tags=['story_without_Token']) 
# # def read_all_posts( skip: int = 0, limit: int = 10):  
    
# #     # DB연결
# #     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
# #     db = myclient["test"]["story_db"]

# #     # TODO: decoded token and the author info are needed
# #     # content = db.find({},{"author": "decoded token"})
# #     content = db.find()

# #     return_list = []
# #     j=0
# #     for i in content:
# #         return_list.append(i)
# #         j+=1
# #         print(f"content{j}: ", i)

# #     print("List : ",return_list)
# #     json_list = json.loads(json_util.dumps(return_list))
# #     print("List in Json : ", json_list)
# #     return json_list

# # update a story post with token
# @router.put("/posts/{id}", tags=['story'])
# def update_post( id: str, post: StoryPost, token: str = Header()):
#     try :
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
#     except:
#         raise HTTPException(status_code=401, detail='Invalid token')

#     print("payload : ",payload)

#     if 'email' in payload:
#         author = payload['email']
#     else:
#         author = payload['sub']
    
#         # 사전 유효성 검사
#     degree_list = ["nobase", "elementary", "middle", "high", "university"]
#     on_offline_list = ["online", "offline", "on_offline", "visit", "outside"]
#     class_contents_list = ["phonics", "reading", "toeic_ielts", "business_english", "job_interview", "etc"]
#     advance_list = ["quality", "facilities", "price", "environment", "system"]

#     if not post.degree in degree_list:
#         raise HTTPException(status_code=400, detail="wrong degree input")
   
#     if not post.on_offline in on_offline_list:
#         raise HTTPException(status_code=400, detail="wrong on_offline input")
   
#     if not post.class_contents in class_contents_list:
#         raise HTTPException(status_code=400, detail="wrong class_contents input")

#     if not post.advance in advance_list:
#         raise HTTPException(status_code=400, detail="wrong advance input")
    
#     # DB연결
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")

   
#     #프로그램 관련 DB 연결
#     program_db = myclient['test']['program_db']
#     program_title = post.program_title
#     # 입력받은 값: program_title
#     program_info_db = program_db.find({"program_title": program_title})
#     program_info_db = list(program_info_db)
#     print("program_title_db : ", program_info_db)
#     print("len(program_title_db) : ", len(program_info_db))

#     # program_title 입력이 잘못 되었을 경우
#     if len(program_info_db) != 1:
#         raise HTTPException(status_code=400, detail="wrong program title")
#     print("program_title_count : ",program_db.count_documents({"program_title": post.program_title}))

#     # 참고하는 프로그램 정보
#     program_id = program_info_db[0]['_id']
#     print("program_title_db_id : ", program_id)

#     db = myclient["test"]["story_db"]
#     print("db : ",db)
#     try:
#         if db.count_documents({'$and': [{"_id": ObjectId(id)},{"author": author}]}) > 0:

#             db.update_one({"_id": ObjectId(id)},
#                         {"$set":{"program_title": post.program_title,
#                                 "program_id": program_id,
#                                 "title": post.title,
#                                 "content":post.content,
#                                 "degree": post.degree,
#                                 "on_offline": post.on_offline,
#                                 "class_contents": post.class_contents,
#                                 "advance" : post.advance,
#                                 },
#                         "$currentDate": {"lastModified": True}})

#             print("content : ", db.find_one({"_id": ObjectId(id)}))
#             content = db.find_one({"_id": ObjectId(id)})

#             return content
#     except IndexError:
#         raise HTTPException(status_code=404, detail="Post not found")

# # delete a story post with token
# @router.delete("/posts/{id}", tags=['story'])
# async def delete_post(id: str, token: str = Header()):
#     try :
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
#     except:
#         raise HTTPException(status_code=401, detail='Invalid token')

#     print("payload : ",payload)

#     if 'email' in payload:
#         author = payload['email']
#     else:
#         author = payload['sub']
    
#     # DB연결
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     db = myclient["test"]["story_db"]
    
#     try:
#         if db.count_documents({'$and': [{"_id": ObjectId(id)},{"author": author}]}) > 0:

#             db.delete_one({"_id": ObjectId(id)})
#             # print("content : ",content.raw_result)
#             return {f"content_id : {id} ": "delete successed"}

#         raise HTTPException(status_code=404, detail="Post not found")
        
#     except IndexError:
#         raise HTTPException(status_code=404, detail="Post not found")


# # 모든 스토리 보기 함수(토큰x, 페이징 처리)
# @router.get("/readall/pagination",  tags=['story_without_Token'])
# def story_list(page: int = Query(1, description="Page number", ge=1), limit = 10):
    
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     db = myclient["test"]["story_db"]

#     # 한 페이지 당 몇 개의 게시물을 출력할 것인가
#     # limit = 3

#     datas = db.find({}).skip((page - 1) * limit).limit(limit)  # program_db 컬럭션에 있는 모든 데이터를 가져옴

#     print("datas: ", datas)

#     # 게시물의 총 개수 세기
#     tot_count = db.count_documents({})

#     print("tot_count: ", tot_count)

#     # 마지막 페이지의 수 구하기
#     last_page_num = math.ceil(tot_count / limit) # 반드시 올림을 해줘야함

#     print("last_page_num: ", last_page_num)

#     # 페이지 블럭을 5개씩 표기
#     block_size = 5

#     # 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
#     block_num = int((page - 1) / block_size)
#     print("block_num: ", block_num)

#     # 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
#     block_start = (block_size * block_num) + 1
#     print("block_start: ", block_start)

#     # 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
#     block_end = block_start + (block_size - 1)
#     print("block_end: ", block_end)

#     return_list = []
#     j=0
#     for i in datas:
#         return_list.append(i)
#         j+=1
#         # print(f"datas{j}: ", i)

#     json_list = json.loads(json_util.dumps(return_list))
#     print("List in Json : ", json_list)

#     return {"limit": limit, "page": page, "block_start": block_start, "block_end": block_end, "last_page_num": last_page_num, "List_in_Json": json_list}

# # read posts, token x
# import math
# # 모든 프로그램 보기 함수(토큰x, 페이지 추가)
# @router.get("/posts")
# def programs_list(page: int = Query(1, description="Page number", ge=1)):
    
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     db = myclient["test"]["story_db"]

#     #####
#     # 한 페이지 당 몇 개의 게시물을 출력할 것인가
#     limit = 3

#     datas = db.find({}).skip((page - 1) * limit).limit(limit)  # program_db 컬럭션에 있는 모든 데이터를 가져옴

#     print("datas: ", datas)

#     # 게시물의 총 개수 세기
#     tot_count = db.count_documents({})

#     print("tot_count: ", tot_count)

#     # 마지막 페이지의 수 구하기
#     last_page_num = math.ceil(tot_count / limit) # 반드시 올림을 해줘야함

#     print("last_page_num: ", last_page_num)

#     if last_page_num < page:    # 페이지 번호가 마지막 페이지 수보다 클때 에러 발생
#         raise HTTPException(
#                     status_code = 400,detail=f'last pagination is {last_page_num}, page number should be less than last page number')

#     # 페이지 블럭을 5개씩 표기
#     block_size = 5

#     # 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
#     block_num = int((page - 1) / block_size)
#     print("block_num: ", block_num)

#     # 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
#     block_start = (block_size * block_num) + 1
#     print("block_start: ", block_start)

#     # 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
#     block_end = block_start + (block_size - 1)
#     print("block_end: ", block_end)

#     return_list = []
#     j=0
#     for i in datas:
#         return_list.append(i)
#         j+=1
#         # print(f"datas{j}: ", i)

#     json_list = json.loads(json_util.dumps(return_list))
#     print("List in Json : ", json_list)

#     return {"limit": limit, "page": page, "block_start": block_start, "block_end": block_end, "last_page_num": last_page_num, "List_in_Json": json_list}






