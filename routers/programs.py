from fastapi import FastAPI, Header, HTTPException, APIRouter, Request, Body, Form, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import pydantic
import jwt
import json
import pymongo
from bson import json_util
from bson.objectid import ObjectId
from enum import Enum

from dataclasses import dataclass

pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

router = APIRouter()

class Programs(BaseModel):
    program_title:str # essential, 프로그램 이름
    program_description:str 
    period_for_reservation_start : datetime| str # essential, 예약 시간 시작
    period_for_reservation_end:datetime | str # essential, 예약 시간 종료 
    period_for_class_start : datetime | str # essential, 프로그램 진행 시간 시작
    period_for_class_end : datetime | str # essential, 프로그램 진행 시간 종료
    url: str = None # essential, 이미지 url
    count_for_like : int = 0 # non-essential, 좋아요 수
    count_for_purchase : int = 0 # non-essential, 참여/결제된 수
    program_price : int # essential, 프로그램 금액
    degree: str # essential, 회원 등급
    on_offline: str # essential, 수업 방식
    class_contents: str # essential, 수업 내용
    advance : str # essential, 기존 조건
    created_at: datetime = datetime.now() # essential, 생성 날짜
    updated_at: datetime| None = None # non-essential, 수정 날짜

    class config:
        schema_extra = {
        'program_title': 'program title',
        'program_description': 'program_description',
        'period_for_reservation_start' : datetime.now().strftime("%Y%m%d%H%M%S"),
        'period_for_reservation_end': (datetime.now() + timedelta(days=7)).strftime("%Y%m%d%H%M%S"),
        'period_for_class_start' : (datetime.now() + timedelta(days=8)).strftime("%Y%m%d%H%M%S"),
        'period_for_class_end' : (datetime.now() + timedelta(days=15)).strftime("%Y%m%d%H%M%S"),
        'program_price' : 0,
        "created_at" : datetime.now().strftime("%Y%m%d%H%M%S"),
        "degree": "nobase",
        "on_offline": "online",
        "class_contents": "reading",
        "advance" :"quality"
        }

class Degree(str): ## 회원 등급
    nobase: str = "nobase" 
    elementary: str = "elementary"
    middle: str = "middle"
    high: str = "high"
    university: str = "university"

class on_offline(str): ## 수업 방식
    online: str = "online"
    offline: str = "offline"
    on_offline: str = "on_offline"
    visit: str = "visit"
    outisde: str = "outisde"

class Class_contents(str): ## 수업 내용
    phonics: str = "phonics"
    reading: str = "reading"
    toeic_ielts: str = "toeic_ielts"
    business_english: str = "business_english"
    job_interview: str = "job_interview"
    etc: str = "etc"

class Advance(str): ## 기존 조건
    quality:str = "quality"
    facilities:str = "facilities"
    price : str = "price"
    environment : str = "environment"
    system : str = "system"

JWT_SECRET = 'adcec27a3417b2de82130a2c54fc5c65aca0d7fa41b0a01dc310f3c78a62f885'
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 선택으로 검색기능, 페이징 처리
@router.get("/programs/search", tags=["program_without_Token"])
async def search_programs(
                        search_option_degree:Degree = None, 
                        search_option_on_offline:on_offline = None,
                        search_option_class_contents:Class_contents = None,
                        search_option_class_advance:Advance = None,
                        page: int = Query(1, description="Page number", ge=1)
                        ):

    print("first 2 datas : ", search_option_degree, search_option_on_offline)
    print("last 2 datas : ", search_option_class_contents, search_option_class_advance)

    # 페이징: 한 페이지 당 몇 개의 게시물을 출력할 것인가
    limit = 3
 
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]
    print("db is connected.")

    # 입력값이 없을 경우: 모든 데이터 출력
    if search_option_degree is None and search_option_on_offline is None and search_option_class_contents is None and search_option_class_advance is None:
        
        # datas = db.find({}) # 페이징 처리 안할 때
        datas = db.find({}).skip((page - 1) * limit).limit(limit) # 페이징 처리
        print("no input data, return all the data")
        datas = list(datas)
        print(datas)
        return datas  # program_db 컬럭션에 있는 모든 데이터를 가져옴

    option_list = [search_option_degree, search_option_on_offline, search_option_class_contents, search_option_class_advance]
     
    # None값이 아닌 것 걸러내기
    search_option_list = []
    for i in option_list:
        if i is not None:
            search_option_list.append(i)
            print(f"{i} has appended to search_option_list")
    
    # None값이 아닌 것 중에 판단하기 
    query_list= []
    for i in search_option_list:       
        if i == search_option_degree:
            result_1 = {"degree":search_option_degree}
            query_list.append(result_1)
            print("result_1 has appended to query_list.")

        if i == search_option_on_offline:
            result_2 = {"on_offline":search_option_on_offline}
            query_list.append(result_2)
            print("result_2 has appended to query_list.")

        if i == search_option_class_contents:
            result_3 = {"class_contents":search_option_class_contents}
            query_list.append(result_3)
            print("result_3 has appended to query_list.")

        if i == search_option_class_advance:
            result_4 = {"advance":search_option_class_advance}
            query_list.append(result_4)
            print("result_4 has appended to query_list.")
      

    if len(query_list)>=2:
        query = {"$and" : query_list} 
        print(f"{len(query_list)} query was created.")

    else:
        query = query_list[0]
        print("1 query was created.")
        
    # Issue the query to the "documents" collection
    # 검색 결과에서 가져올 데이터만 추린다. 
    results = db.find(query)
    # results = db.find(query).skip((page - 1) * limit).limit(limit)
    results = list(results)
    print("results: ", results)
    print(f"results: {len(results)} results were returned.")

    # 결과값이 없으면
    if len(results) <= 0:
        return {"results": "No data found"}
    

    # limit(한 페이지에 보여주는 결과) 보다 결과값이 적으면, 페이징 처리할 필요가 없음
    if len(results) <= limit:
        return results
    else:
        results = db.find(query).skip((page - 1) * limit).limit(limit)
        
    # limit보다 결과물이 많을 때
    # 페이징: 게시물의 총 개수 세기
    tot_count = len(list(db.find(query)))
    print("tot_count: ", tot_count)

    # 페이징: 마지막 페이지의 수 구하기
    last_page_num = math.ceil(tot_count / limit) # 페이징: 반드시 올림을 해줘야함
    print("last_page_num: ", last_page_num)

    if last_page_num < page:    # 페이징: 페이지 번호가 마지막 페이지 수보다 클때 에러 발생
        raise HTTPException(
                    status_code = 400,detail=f'last pagination is {last_page_num}, page number should be less than last page number')

    # 페이징: 페이지 블럭을 5개씩 표기
    block_size = 5

    # 페이징: 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
    block_num = int((page - 1) / block_size)
    print("block_num: ", block_num)

    # 페이징: 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
    block_start = (block_size * block_num) + 1
    print("block_start: ", block_start)

    # 페이징: 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
    block_end = block_start + (block_size - 1)
    print("block_end: ", block_end)
   
    return results


# 텍스트 검색 기능, 페이징 처리
@router.get("/programs/search-text", tags=["program_without_Token"])
async def search_programs(data = None, page: int = Query(1, description="Page number", ge=1)):

    print('data:' ,data)
    # 페이징: 한 페이지 당 몇 개의 게시물을 출력할 것인가
    limit = 3

    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]
    print("db is connected.")

    # 입력값이 없을 경우: 모든 데이터 출력
    if data is None:
        datas = db.find({}).skip((page - 1) * limit).limit(limit)
        print("no data, return all the data")
        datas = list(datas)
        print(datas)
        return datas  # program_db 컬럭션에 있는 모든 데이터를 가져옴

    # 입력값 양쪽 공백 제거
    data = data.strip()
    print("data has trimmed")

    ##### 문자 사이에 공백이 많을 경우 -> 공백 하나로 치환
    # 방법1: replace
    while True:
        if "  " in data:
            data = data.replace("  " , " ")
            print("data blank has replaced as ' '.")
        else:
            print("No more extra blank.")
            break
        
    # 방법2 : 문자열 나누기와 문자열 합치기(split_join)
    # if data 
    # data = ' '.join(data.split())
    # 방법3: 정규표현식(re) 이용하기

    #### TODO 정확한 값일 경우
    #### TODO phrase 값일 경우: 띄어쓰기가 있을 경우
    #### TODO 포함된 값일 경우

    # Build the query
    query = { "$or": [
    {"program_title": {"$regex": data, "$options": "i"}}, # 대소문자 상관없이
    {"program_description": {"$regex": data, "$options": "i"}} ]} # 포함되어있는 데이터
    
    print("query was created.")

    # Issue the query to the "documents" collection
    # 검색 결과에서 가져올 데이터만 추린다. 
    results = db.find(query).skip((page - 1) * limit).limit(limit)
    results = list(results)
    print("data has found.")
    print("results : ", results)

    # 결과값이 없으면
    if len(results) <= 0:
        return {"results": "No data found"}

    # 페이징: 게시물의 총 개수 세기
    tot_count = len(list(db.find(query)))
    print("tot_count: ", tot_count)

    # 페이징: 마지막 페이지의 수 구하기
    last_page_num = math.ceil(tot_count / limit) # 페이징: 반드시 올림을 해줘야함
    print("last_page_num: ", last_page_num)

    if last_page_num < page:    # 페이징: 페이지 번호가 마지막 페이지 수보다 클때 에러 발생
        raise HTTPException(
                    status_code = 400,detail=f'last pagination is {last_page_num}, page number should be less than last page number')

    # 페이징: 페이지 블럭을 5개씩 표기
    block_size = 5

    # 페이징: 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
    block_num = int((page - 1) / block_size)
    print("block_num: ", block_num)

    # 페이징: 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
    block_start = (block_size * block_num) + 1
    print("block_start: ", block_start)

    # 페이징: 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
    block_end = block_start + (block_size - 1)
    print("block_end: ", block_end)

    # return_list = []
    # j=0
    # for i in datas:
    #     return_list.append(i)
    #     j+=1
    #     # print(f"datas{j}: ", i)

    # json_list = json.loads(json_util.dumps(return_list))
    # print("List in Json : ", json_list)

    return {"page_limit": limit, 
            "page": page, 
            "block_start": block_start,
            "block_end": block_end, 
            "last_page_num": last_page_num, 
            "List_in_Json": results}
    # return results 

import math
# 모든 프로그램 보기 함수(토큰x, 페이지 추가)
@router.get("/programs/readall/pagination",  tags=['program_without_Token'])
def programs_list(page: int = Query(1, description="Page number", ge=1)):
    
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]

    #####
    # 한 페이지 당 몇 개의 게시물을 출력할 것인가
    limit = 3

    datas = db.find({}).skip((page - 1) * limit).limit(limit)  # program_db 컬럭션에 있는 모든 데이터를 가져옴

    print("datas: ", datas)

    # 게시물의 총 개수 세기
    tot_count = db.count_documents({})

    print("tot_count: ", tot_count)

    # 마지막 페이지의 수 구하기
    last_page_num = math.ceil(tot_count / limit) # 반드시 올림을 해줘야함

    print("last_page_num: ", last_page_num)

    if last_page_num < page:    # 페이지 번호가 마지막 페이지 수보다 클때 에러 발생
        raise HTTPException(
                    status_code = 400,detail=f'last pagination is {last_page_num}, page number should be less than last page number')

    # 페이지 블럭을 5개씩 표기
    block_size = 5

    # 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
    block_num = int((page - 1) / block_size)
    print("block_num: ", block_num)

    # 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
    block_start = (block_size * block_num) + 1
    print("block_start: ", block_start)

    # 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
    block_end = block_start + (block_size - 1)
    print("block_end: ", block_end)

    return_list = []
    j=0
    for i in datas:
        return_list.append(i)
        j+=1
        # print(f"datas{j}: ", i)

    json_list = json.loads(json_util.dumps(return_list))
    print("List in Json : ", json_list)

    return {"limit": limit, "page": page, "block_start": block_start, "block_end": block_end, "last_page_num": last_page_num, "List_in_Json": json_list}

# # 모든 프로그램 보기 (토큰x)
# @router.get("/programs/readall",  tags=['program_without_Token']) 
# def read_all_programs ( skip: int = 0, limit: int = 10):  
    
#     # DB연결
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     db = myclient["test"]["program_db"]

#     content = db.find()

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


# read a single program post without token
@router.get("/programs/posts/{id}/test", tags=['program_without_Token']) 
async def read_single_program(id: str): 
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]

    try:
        content = db.find_one({"_id": ObjectId(id)})
        print("content : ", content)
        return content

    except IndexError:
        raise HTTPException(status_code=404, detail="wrong program_id")

# read a single program post with token
@router.get("/programs/posts/{id}") 
async def read_single_program(id: str, token: str = Header()): 
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["story_db"]

    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    print("payload : ",payload)

    if 'email' in payload:
        author = payload['email']
    else:
        author = payload['sub']

    try:
        content = db.find_one({'$and': [{"_id": ObjectId(id)},{"author": author}]})
        print("content : ", content)
        return content

    except IndexError:
        raise HTTPException(status_code=400, detail="Post not found")

# 프로그램 추가(토큰 없이 테스트)
@router.post("/programs/posts/test", tags=['programs'])
async def create_programs(request: Request = Body()) :
    # Request Object를 직접 가져오면, FastAPI에 의해 유효성 검사와 문서화가 되지 않는다. 
    print('request : ', request)

    data = await request.json() # TODO: 왜 되는지 모르겠다.
    print('data2:' ,data)
    print('program_title : ', data['program_title'])
    
    programs = data

    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]
    
    title = programs['program_title']
    description = programs['program_description']
    period_for_reservation_start = programs['period_for_reservation_start']
    period_for_reservation_end = programs['period_for_reservation_end']

    if period_for_reservation_start > period_for_reservation_end:
        raise HTTPException(
                    status_code=400,detail='The reservation start day should be before the end day.')

    period_for_class_start = programs['period_for_class_start']
    period_for_class_end = programs['period_for_class_end']

    if period_for_class_start > period_for_class_end:
        raise HTTPException(
                    status_code=400,detail='The class start day should be before the end day.')
    price = programs['program_price']
    degree = programs['degree']
    on_offline = programs['on_offline']
    class_contents = programs['class_contents']
    advance = programs['advance']

    data = {
        'program_title': title,
        'program_description': description,
        'period_for_reservation_start' : period_for_reservation_start,
        'period_for_reservation_end': period_for_reservation_end,
        'period_for_class_start' : period_for_class_start,
        'period_for_class_end' : period_for_class_end,
        'program_price' : price,
        "degree": degree,
        "on_offline": on_offline,
        "class_contents": class_contents,
        "advance" :advance,
        "created_at" : datetime.now()}

    content = db.insert_one(data)
    # print("content : ", content)
    content_id = content.inserted_id
    print("content_id : ",content_id)
    print("content : ", db.find_one({"_id": ObjectId(content_id)}))
    
    return {"programs_id":'content_id' }

# 프로그램 추가
@router.post("/programs/posts", tags=['programs'])
async def create_programs(request: Request = Body(), token: str = Header()):
    print('request : ', request)

    programs = await request.json() # TODO: 왜 되는지 모르겠다.
    print('data2:' ,programs )
    print('program_title : ', programs['program_title'])
 
    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    print("payload : ",payload)

    if 'email' in payload:
        email = payload['email']
    else:
        email = payload['sub']
    
    if email != 'admin@gmail.com': # 관리자만 작성할 수 있음. 
        raise HTTPException(status_code=400, detail='Not authorized account ')

    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]
   
    title = programs['program_title']
    description = programs['program_description']
    period_for_reservation_start = programs['period_for_reservation_start']
    period_for_reservation_end = programs['period_for_reservation_end']

    if period_for_reservation_start > period_for_reservation_end:
        raise HTTPException(
                    status_code=400,detail='The reservation start day should be before the end day.')

    period_for_class_start = programs['period_for_class_start']
    period_for_class_end = programs['period_for_class_end']

    if period_for_class_start > period_for_class_end:
        raise HTTPException(
                    status_code=400,detail='The class start day should be before the end day.')
    price = programs['program_price']
    degree = programs['degree']
    on_offline = programs['on_offline']
    class_contents = programs['class_contents']
    advance = programs['advance']

    data = {
        'program_title': title,
        'program_description': description,
        'period_for_reservation_start' : period_for_reservation_start,
        'period_for_reservation_end': period_for_reservation_end,
        'period_for_class_start' : period_for_class_start,
        'period_for_class_end' : period_for_class_end,
        'program_price' : price,
        "degree": degree,
        "on_offline": on_offline,
        "class_contents": class_contents,
        "advance" :advance,
        "created_at" : datetime.now()}

    content = db.insert_one(data)
    # print("content : ", content)
    content_id = content.inserted_id
    print("content_id : ",content_id)
    print("content : ", db.find_one({"_id": ObjectId(content_id)}))
   
    return {"programs_id":'content_id' }

# 프로그램 수정
@router.put("/programs/posts/{id}", tags=['programs'])
def update_program_post( id: str, programs: Programs, token: str = Header()):

    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    except:
        raise HTTPException(status_code=401, detail='Invaild token')

    print("payload : ",payload)

    if 'email' in payload:
        email = payload['email']
    else:
        email = payload['sub']
    
    if email != 'admin@gmail.com': # 관리자만 작성할 수 있음. 
        raise HTTPException(status_code=401, detail='Not authorized account')

    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]
    
    period_for_reservation_start = programs.period_for_reservation_start
    period_for_reservation_end = programs.period_for_reservation_end

    if period_for_reservation_start > period_for_reservation_end:
        raise HTTPException(
                    status_code=400,detail='The reservation start day should be before the end day.')

    period_for_class_start = programs.period_for_class_start
    period_for_class_end = programs.period_for_class_end

    if period_for_class_start > period_for_class_end:
        raise HTTPException(
                    status_code=400,detail='The class start day should be before the end day.')

    print("db : ",db)
    try:
        if db.count_documents({"_id": ObjectId(id)}) > 0: # 관리자인 다른 사람도 수정할 수 있음. 

            db.update_one({"_id": ObjectId(id)},
                        {"$set":{"program_title":programs.program_title,
                        "program_description":programs.program_description,
                        'period_for_reservation_start' : programs.period_for_reservation_start,
                        'period_for_reservation_end': programs.period_for_reservation_end,
                        'period_for_class_start' : programs.period_for_class_start,
                        'period_for_class_end' : programs.period_for_class_end,
                        'program_price' : programs.program_price,
                        "degree": programs.degree,
                        "on_offline": programs.on_offline,
                        "class_contents": programs.class_contents,
                        "advance" :programs.advance,
                        },
                        "$currentDate": {"lastModified": True}})

            print("content : ", db.find_one({"_id": ObjectId(id)}))

            content = db.find_one({"_id": ObjectId(id)})

            return {"update_program_post_id": id}
    except IndexError:
        raise HTTPException(status_code=404, detail="Post not found")

# 프로그램 삭제
@router.delete("/programs/posts/{id}", tags=['programs'])
async def delete_program_post(id: str, token: str = Header()):
    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    except:
        raise HTTPException(status_code=401, detail='Invaild token')

    print("payload : ",payload)

    if 'email' in payload:
        email = payload['email']
    else:
        email = payload['sub']
    
    if email != 'admin@gmail.com': # 관리자만 권한 있음. 
        raise HTTPException(status_code=401, detail='Not authorized account ')

    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]
    
    
    try:
        if db.count_documents({'$and': [{"_id": ObjectId(id)},{"email": email}]}) > 0:

            db.delete_one({"_id": ObjectId(id)})
            return {"deleted_program_id ": id}

        raise HTTPException(status_code=404, detail="Program Post not found")
        
    except IndexError:
        raise HTTPException(status_code=404, detail="Program Post not found")



# 댓글 DB 스키마
class Comments(BaseModel):
    program_post_id: str # essential
    email:str # essential
    nickname : str | None # non-essential
    content: str = Field(max_length=300) # essential

    class config:
        schema_extra = {
        'program_post_id': 'Refered program_post_id',
        'content': 'comment maximum 300 letters'}

# 댓글 추가
@router.post("/comments/posts", tags=['comments'])
def create_comment(comments: Comments, token: str = Header()):
    print(comments)
    print(len(comments.content)) # pydantic이 최대 글자수를 넘는 순간 에러를 발생시킨다.

    # if len(comments.content) > 300:
    #     raise HTTPException(status_code=400, detail='Maximum 300 letters')

    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    print("payload : ",payload)

    if 'email' in payload:
        email = payload['email']
    else:
        email = payload['sub']
    
    if 'nickname' in payload:
        nickname = payload['nickname']
    else:
        nickname = None
    
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["comment_db"]

    data = {
        'program_post_id': comments.program_post_id,
        'email': email,
        'nickname' : nickname,
        'comment': comments.content,
        "created_at" : datetime.now()}
    
    content = db.insert_one(data)

    content_id = content.inserted_id
    print("content_id : ",content_id)
    print("content : ", db.find_one({"_id": ObjectId(content_id)}))
    
    return {"comment_id":content_id }

# 댓글 전체 읽기
@router.get("/comments/posts", tags=['comments']) 
def read_all_comments( skip: int = 0, limit: int = 20):  
    
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["comment_db"]

    content = db.find()

    return_list = []
    j=0
    for i in content:
        return_list.append(i)
        j+=1
        print(f"content{j}: ", i)

    print("List : ",return_list)
    json_list = json.loads(json_util.dumps(return_list))
    print("List in Json : ", json_list)
    return json_list

# 댓글 수정
@router.put("/comments/posts/{id}", tags=['comments'])
def update_comment_post(id: str, comments: Comments, token: str = Header()):

    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    print("payload : ",payload)

    if 'email' in payload:
        email = payload['email']
    else:
        email = payload['sub']
    
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["comment_db"]

    try:
        if db.count_documents({'$and': [{"_id": ObjectId(id)},{"email": email}]}) > 0:
            db.update_one({"_id": ObjectId(id)},
                                    {"$set":{"comment": comments.content},
                                    "$currentDate": {"lastModified": True}})

            content = db.find_one({"_id": ObjectId(id)})
            print("content : ",content)

            return {"update_program_post_id": id}

    except IndexError:
        raise HTTPException(status_code=404, detail="Post not found")

# 댓글 삭제
@router.delete("/comments/posts/{id}", tags=['comments'])
async def delete_post(id: str, token: str = Header()):
    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    print("payload : ",payload)

    if 'email' in payload:
        email = payload['email']
    else:
        email = payload['sub']
    
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["story_db"]
    
    try:
        if db.count_documents({'$and': [{"_id": ObjectId(id)},{"email": email}]}) > 0:

            db.delete_one({"_id": ObjectId(id)})
            return {f"content_id : {id} ": "delete successed"}
        raise HTTPException(status_code=404, detail="Comment not found")
        
    except IndexError:
        raise HTTPException(status_code=404, detail="Comment not found")

# 좋아요 
