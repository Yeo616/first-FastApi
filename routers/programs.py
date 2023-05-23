from fastapi import FastAPI, Header, HTTPException, APIRouter, Request, UploadFile, File, Body, Form, Query
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
import logging
import math
import uuid
import os

pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

router = APIRouter()

# 로그 생성
logger = logging.getLogger('programs')                                               # Logger 인스턴스 생성, 命名
logger.setLevel(logging.DEBUG)                                                       # Logger 출력 기준 설정
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')# Formatter 생성, log 출력 형식

# log 출력
StreamHandler = logging.StreamHandler()                                              # 콘솔 출력 핸들러 생성
StreamHandler.setFormatter(formatter)                                                
logger.addHandler(StreamHandler)    

class Programs(BaseModel):
    program_title:str # essential, 프로그램 이름
    program_description:str  # essential, 프로그램 설명 
    period_for_reservation_start : datetime| str # essential, 예약 시간 시작
    period_for_reservation_end:datetime | str # essential, 예약 시간 종료 
    period_for_class_start : datetime | str # essential, 프로그램 진행 시간 시작
    period_for_class_end : datetime | str # essential, 프로그램 진행 시간 종료
    
    img: str | None = None # non-essential, 스토리 삽입 대표 이미지
    img_db_id: str | None = None # non-essential, 스토리 삽입 이미지    
    
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
        'period_for_reservation_start' : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'period_for_reservation_end': (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
        'period_for_class_start' : (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S"),
        'period_for_class_end' : (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S"),
        'program_price' : 0,
        "created_at" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
    outside: str = "outside"

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

    logger.info(f'first 2 datas : {search_option_degree}, {search_option_on_offline}')
    logger.info(f'last 2 datas : {search_option_class_contents}, {search_option_class_advance}')

    # 페이징: 한 페이지 당 몇 개의 게시물을 출력할 것인가
    limit = 3
 
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]

    logger.info('db is connected')

    # 입력값이 없을 경우: 모든 데이터 출력
    if search_option_degree is None and search_option_on_offline is None and search_option_class_contents is None and search_option_class_advance is None:
        
        # datas = db.find({}) # 페이징 처리 안할 때
        datas = db.find({}).sort('created_at',-1).skip((page - 1) * limit).limit(limit) # 페이징 처리

        logger.info('no input data, return all the data')
        
        datas = list(datas)

        logger.info(f'data : {datas}')

        return datas  # program_db 컬럭션에 있는 모든 데이터를 가져옴

    option_list = [search_option_degree, search_option_on_offline, search_option_class_contents, search_option_class_advance]
     
    # None값이 아닌 것 걸러내기
    search_option_list = []
    for i in option_list:
        if i is not None:
            search_option_list.append(i)
            logger.info(f"{i} has appended to search_option_list")
    
    # None값이 아닌 것 중에 판단하기 
    query_list= []
    for i in search_option_list:       
        if i == search_option_degree:
            result_1 = {"degree":search_option_degree}
            query_list.append(result_1)
            logger.info("result_1 has appended to query_list.")

        if i == search_option_on_offline:
            result_2 = {"on_offline":search_option_on_offline}
            query_list.append(result_2)
            logger.info("result_2 has appended to query_list.")

        if i == search_option_class_contents:
            result_3 = {"class_contents":search_option_class_contents}
            query_list.append(result_3)
            logger.info("result_3 has appended to query_list.")

        if i == search_option_class_advance:
            result_4 = {"advance":search_option_class_advance}
            query_list.append(result_4)
            logger.info("result_4 has appended to query_list.")
      

    if len(query_list)>=2:
        query = {"$and" : query_list} 
        logger.info(f"{len(query_list)} query was created.")

    else:
        query = query_list[0]
        logger.info("1 query was created.")

    # Issue the query to the "documents" collection
    # 검색 결과에서 가져올 데이터만 추린다. 
    results = db.find(query).sort('created_at',-1)
    # results = db.find(query).skip((page - 1) * limit).limit(limit)
    results = list(results)
    
    logger.info(f"results : {results}")
    logger.info(f"results: {len(results)} results were returned.")

    # 결과값이 없으면
    if len(results) <= 0:
        return {"results": "No data found"}
    
    # limit(한 페이지에 보여주는 결과) 보다 결과값이 적으면, 페이징 처리할 필요가 없음
    if len(results) <= limit:
        return results
    else:
        results = db.find(query).sort('created_at',-1).skip((page - 1) * limit).limit(limit)
        results = list(results)
        
    # limit보다 결과물이 많을 때
    # 페이징: 게시물의 총 개수 세기
    tot_count = len(list(db.find(query)))
    logger.info(f"tot_count : {tot_count}")

    # 페이징: 마지막 페이지의 수 구하기
    last_page_num = math.ceil(tot_count / limit) # 페이징: 반드시 올림을 해줘야함
    logger.info(f"last_page_num : {last_page_num}")

    if last_page_num < page:    # 페이징: 페이지 번호가 마지막 페이지 수보다 클때 에러 발생
        logger.error(f"last_page_num : {last_page_num} < page : {page}")
        raise HTTPException(
                    status_code = 400,detail=f'last pagination is {last_page_num}, page number should be less than last page number')

    # 페이징: 페이지 블럭을 5개씩 표기
    block_size = 5

    # 페이징: 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
    block_num = int((page - 1) / block_size)
    logger.info(f"block_num : {block_num}")

    # 페이징: 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
    block_start = (block_size * block_num) + 1
    logger.info(f"block_start : {block_start}")

    # 페이징: 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
    block_end = block_start + (block_size - 1)
    logger.info(f"block_end : {block_end}")
   
    return results

# 텍스트 검색 기능, 페이징 처리
@router.get("/programs/search-text", tags=["program_without_Token"])
async def search_programs(data = None, page: int = Query(1, description="Page number", ge=1)):

    logger.info(f"data : {data}")
    # 페이징: 한 페이지 당 몇 개의 게시물을 출력할 것인가
    limit = 3

    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]
    logger.info("db is connected.")

    # 입력값이 없을 경우: 모든 데이터 출력
    if data is None:
        datas = db.find({}).sort('created_at',-1).skip((page - 1) * limit).limit(limit)
        logger.info("no data, return all the data")

        datas = list(datas)
        logger.info(f"datas : {datas}")
        return datas# program_db 컬럭션에 있는 모든 데이터를 가져옴

    # 입력값 양쪽 공백 제거
    data = data.strip()
    logger.info("data has trimmed")

    ##### 문자 사이에 공백이 많을 경우 -> 공백 하나로 치환
    # 방법1: replace
    while True:
        if "  " in data:
            data = data.replace("  " , " ")
            logger.info("data blank has replaced as ' '.")
        else:
            logger.info("No more extra blank.")
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
    
    logger.info("query was created.")

    # Issue the query to the "documents" collection
    # 검색 결과에서 가져올 데이터만 추린다. 
    results = db.find(query).skip((page - 1) * limit).limit(limit)
    results = list(results)
    logger.info("data has found.")
    logger.info(f"results : {results}[0]")

    # 결과값이 없으면
    if len(results) <= 0:
        return {"results": "No data found"}

    # 페이징: 게시물의 총 개수 세기
    tot_count = len(list(db.find(query)))
    logger.info(f"tot_count : {tot_count}")

    # 페이징: 마지막 페이지의 수 구하기
    last_page_num = math.ceil(tot_count / limit) # 페이징: 반드시 올림을 해줘야함
    logger.info(f"last_page_num : {last_page_num}")

    if last_page_num < page:    # 페이징: 페이지 번호가 마지막 페이지 수보다 클때 에러 발생
        logger.error("last_page_num: {last_page_num} <page: {page}")
        raise HTTPException(
                    status_code = 400,detail=f'last pagination is {last_page_num}, page number should be less than last page number')

    # 페이징: 페이지 블럭을 5개씩 표기
    block_size = 5

    # 페이징: 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
    block_num = int((page - 1) / block_size)
    logger.info(f"block_num: {block_num}")

    # 페이징: 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
    block_start = (block_size * block_num) + 1
    logger.info(f"block_start : {block_start}")

    # 페이징: 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
    block_end = block_start + (block_size - 1)
    logger.info(f"block_end : {block_end}")

    # return_list = []
    # j=0
    # for i in datas:
    #     return_list.append(i)
    #     j+=1
    #     # logger.info(f"datas{j}: ", i)

    # json_list = json.loads(json_util.dumps(return_list))
    # logger.info(f"List in Json : {json_list}")

    return {"page_limit": limit, 
            "page": page, 
            "block_start": block_start,
            "block_end": block_end, 
            "last_page_num": last_page_num, 
            "List_in_Json": results}
    # return results 

# # 모든 프로그램 보기 함수(토큰x, 페이지 추가)
# @router.get("/programs/readall/pagination",  tags=['program_without_Token'])
# def programs_list(page: int = Query(1, description="Page number", ge=1)):
    
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     db = myclient["test"]["program_db"]

#     #####
#     # 한 페이지 당 몇 개의 게시물을 출력할 것인가
#     limit = 3

#     datas = db.find({}).sort('created_at',-1).skip((page - 1) * limit).limit(limit)  # program_db 컬럭션에 있는 모든 데이터를 가져옴

#     logger.info(f"datas: {datas}")

#     # 게시물의 총 개수 세기
#     tot_count = db.count_documents({})

#     logger.info(f"tot_count: {tot_count}")

#     # 마지막 페이지의 수 구하기
#     last_page_num = math.ceil(tot_count / limit) # 반드시 올림을 해줘야함

#     logger.info(f"last_page_num: {last_page_num}")

#     if last_page_num < page:    # 페이지 번호가 마지막 페이지 수보다 클때 에러 발생
#         logger.error(f"last_page_num : {last_page_num} < page : {page}")
#         raise HTTPException(
#                     status_code = 400,detail=f'last pagination is {last_page_num}, page number should be less than last page number')

#     # 페이지 블럭을 5개씩 표기
#     block_size = 5

#     # 현재 블럭의 위치 (첫 번째 블럭이라면, block_num = 0)
#     block_num = int((page - 1) / block_size)
#     logger.info(f"block_num: {block_num}")

#     # 현재 블럭의 맨 처음 페이지 넘버 (첫 번째 블럭이라면, block_start = 1, 두 번째 블럭이라면, block_start = 6)
#     block_start = (block_size * block_num) + 1
#     logger.info(f"block_start: {block_start}")

#     # 현재 블럭의 맨 끝 페이지 넘버 (첫 번째 블럭이라면, block_end = 5)
#     block_end = block_start + (block_size - 1)
#     logger.info(f"block_end: {block_end}")

#     return_list = []
#     j=0
#     for i in datas:
#         return_list.append(i)
#         j+=1
#         # logger.info(f"datas{j}: ", i)

#     json_list = json.loads(json_util.dumps(return_list))
#     logger.info(f"List in Json : {json_list}")

#     return {"limit": limit, "page": page, "block_start": block_start, "block_end": block_end, "last_page_num": last_page_num, "List_in_Json": json_list}

# # 모든 프로그램 보기 (토큰x)
# @router.get("/programs/readall",  tags=['program_without_Token']) 
# def read_all_programs ( skip: int = 0, limit: int = 10):  
    
#     # DB연결
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     db = myclient["test"]["program_db"]

#     content = db.find({}).sort('created_at',-1)

#     return_list = []
#     j=0
#     for i in content:
#         return_list.append(i)
#         j+=1
#         logger.info(f"content{j}: ", i)

#     logger.info(f"List : {return_list}")

#     json_list = json.loads(json_util.dumps(return_list))
#     logger.info(f"List in Json : {json_list}")
#     return json_list

# 하나의 프로그램 게시물 읽기(토큰x)
@router.get("/programs/posts/{id}", tags=['program_without_Token']) 
async def read_single_program(id: str): 
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]

    try:
        content = db.find_one({"_id": ObjectId(id)})
        logger.info(f"content : {content}")
        return content

    except IndexError:
        raise HTTPException(status_code=404, detail="wrong program_id")

# 하나의 프로그램 게시물 읽기(토큰o) -> 비공개 게시물 등
@router.get("/programs/posts/token/{id}") 
async def read_single_program_token(id: str, token: str = Header()): 
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]

    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    logger.info(f"payload : {payload}")

    if 'email' in payload:
        email = payload['email']
    else:
        email = payload['sub']
    
    admin_list = ['admin@gmail.com']
    if not email in admin_list:
        raise HTTPException(status_code=401, detail='Only admin accounts are permitted')

    try: 
        # 어차피 관리자만 작성가능함. 
        content = db.find_one({'$and': {"_id": ObjectId(id)}})
        logger.info(f"content : {content}")
        return content

    except IndexError:
        logger.error("Post not found")
        raise HTTPException(status_code=400, detail="Post not found")

# 프로그램 추가(토큰x)
@router.post("/programs/posts/test", tags=['program_without_Token'])
async def create_programs(
        program_title:Request = Form(...), # essential, 프로그램 이름
        program_description:Request = Form(...), # essential, 프로그램 설명 
        period_for_reservation_start : Request = Form(...) , # essential, 예약 시간 시작
        period_for_reservation_end:Request  = Form(...) ,# essential, 예약 시간 종료 
        period_for_class_start : Request  = Form(...) ,# essential, 프로그램 진행 시간 시작
        period_for_class_end : Request  = Form(...),# essential, 프로그램 진행 시간 종료
        program_price : int= Form(...), # essential, 프로그램 금액
        degree: str = Form(...),# essential, 회원 등급
        on_offline: str = Form(...),# essential, 수업 방식
        class_contents: str = Form(...),# essential, 수업 내용
        advance : str = Form(...),# essential, 기존 조건
        files: UploadFile = File(default=None)  
        # request: Request = Body() # Request Object를 직접 가져오면, FastAPI에 의해 유효성 검사와 문서화가 되지 않는다. 
                            ) :
 
    logger.info(f"had input : program title: {program_title}, program_description : {program_description}, period_for_reservation_start : {period_for_reservation_start}, period_for_reservation_end: {period_for_reservation_end}, period_for_class_start : {period_for_class_start}, period_for_class_end : {period_for_class_end}, program_price: {program_price}")
    logger.info(f"had input : degree: {degree}, on_offline : {on_offline}, class_contents : {class_contents}, advance: {advance}")
    logger.info(f"files : {files}")

    logger.info("accepted")
    # 시간 형식 맞추기
    datetime_format = '%Y-%m-%d'
    period_for_reservation_start = str(period_for_reservation_start)
    period_for_reservation_start = datetime.strptime(period_for_reservation_start,datetime_format)
    logger.info(f"period_for_reservation_start: {period_for_reservation_start}")

    period_for_reservation_end = str(period_for_reservation_end)
    period_for_reservation_end = datetime.strptime(period_for_reservation_end,datetime_format)
    logger.info(f"period_for_reservation_end: {period_for_reservation_end}")

    period_for_class_start = str(period_for_class_start)
    period_for_class_start = datetime.strptime(period_for_class_start,datetime_format)
    logger.info(f"period_for_class_start: {period_for_class_start}")

    period_for_class_end = str(period_for_class_end)
    period_for_class_end = datetime.strptime(period_for_class_end,datetime_format)
    logger.info(f"period_for_class_end: {period_for_class_end}")

    # 사전 유효성 검사
    degree_list = ["nobase", "elementary", "middle", "high", "university"]
    on_offline_list = ["online", "offline", "on_offline", "visit", "outside"]
    class_contents_list = ["phonics", "reading", "toeic_ielts", "business_english", "job_interview", "etc"]
    advance_list = ["quality", "facilities", "price", "environment", "system"]

    # if not post.degree in degree_list:
    if not degree in degree_list:
        raise HTTPException(status_code=400, detail="wrong degree input")
   
    # if not post.on_offline in on_offline_list:
    if not on_offline in on_offline_list:
        raise HTTPException(status_code=400, detail="wrong on_offline input")
   
    # if not post.class_contents in class_contents_list:
    if not class_contents in class_contents_list:
        raise HTTPException(status_code=400, detail="wrong class_contents input")

    # if not post.advance in advance_list:
    if not advance in advance_list:
        raise HTTPException(status_code=400, detail="wrong advance input")

    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]
    
    if period_for_reservation_start > period_for_reservation_end:
        logger.error("The reservation start day should be before the end day.")
        raise HTTPException(
                    status_code=400,detail='The reservation start day should be before the end day.')

    if period_for_class_start > period_for_class_end:
        logger.error('The class start day should be before the end day.')
        raise HTTPException(
                    status_code=400,detail='The class start day should be before the end day.')

    data = {
        'program_title': program_title,
        'program_description': program_description,
        'period_for_reservation_start' : period_for_reservation_start,
        'period_for_reservation_end': period_for_reservation_end,
        'period_for_class_start' : period_for_class_start,
        'period_for_class_end' : period_for_class_end,
        'program_price' : program_price,
        "degree": degree,
        "on_offline": on_offline,
        "class_contents": class_contents,
        "advance":advance,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    content = db.insert_one(data) # 데이터 입력

    # 생성한 content_id
    content_id = content.inserted_id

    data_in_db = db.find_one({"_id": ObjectId(content_id)})
    logger.info(f"content_id : {content_id}")
    logger.info(f"content : {db.find_one({'_id': ObjectId(content_id)})}")

    if files is None:
        return {"content_id":f"{content_id}", # 스토리 콘텐츠 아이디
                "content_data": data_in_db}   # 스토리 입력 값

    ##============ 이미지 업로드(대표 이미지) ==================
    # 이미지 저장할 경로 지정
    UPLOAD_DIRECTORY = "./saving_images/"
    LOCAL_URL = "http://192.168.1.101:8000"

    # 이미지 DB 연결
    image_db = myclient["test"]["image_db"]

    currentTime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
   
    contents = await files.read() # 파일을 읽는 동안 CPU가 다른 일을 하도록 명령
    saved_file_name = f"{currentTime}{str(uuid.uuid4())}.jpg" # 업로드한 시간과 UUID를 이용해서 유니크한 파일명으로 변경
    saved_file_path = f"{LOCAL_URL}/images/{saved_file_name}" # localhost:8000/ 파일 경로 url

    # DB에 이미지 저장
    image_data = {
            "program_refered_id" : ObjectId(content_id),
            "image_url": saved_file_path,
            "image_name": saved_file_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    image_content = image_db.insert_one(image_data)
    image_content_id = image_content.inserted_id
    logger.info(f"image content_id : {image_content_id}")

    # logger.info(f"original file name: {file.filename}")
    logger.info(f"file_names : {saved_file_name}")
    logger.info(f"file_path: {saved_file_path}")

    
    with open(os.path.join(UPLOAD_DIRECTORY, saved_file_name), "wb") as fp: 
        fp.write(contents) # 로컬에 이미지 저장(쓰기)
   
    # 위에 생성한 program에 img_url 추가하기
    db.update_one({"_id": ObjectId(content_id)},{"$set":{"img": saved_file_path, "img_db_id": ObjectId(image_content_id)}})

    logger.info(f"content_modified : {db.find_one({'_id': ObjectId(content_id)})}")
   
    content_db = db.find_one({"_id": ObjectId(content_id)})

    # 연관된 프로그램 정보도 넘기게 하였음.
    return {
            "file_path": saved_file_path, # 파일 더미에서 각 저장한 경로 및 파일명 호출
            "content_id":f"{content_id}", # 스토리 콘텐츠 아이디
            "content_data": content_db
            }   # 스토리 입력 값
            

# 프로그램 추가 TODO 고쳐야함
@router.post("/programs/posts", tags=['programs'])
async def create_programs(request: Request = Body(), token: str = Header()):
    
    logger.info(f'request : {request}')

    programs = await request.json() # TODO: 왜 되는지 모르겠다.
    logger.info(f'data : {data}')
    logger.info(f"program_title : {data['program_title']}")
    
    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    logger.info(f"payload : {payload}")

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
        logger.error("The reservation start day should be before the end day.")
        raise HTTPException(
                    status_code=400,detail='The reservation start day should be before the end day.')

    period_for_class_start = programs['period_for_class_start']
    period_for_class_end = programs['period_for_class_end']

    if period_for_class_start > period_for_class_end:
        logger.error('The class start day should be before the end day.')
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
        "created_at" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    content = db.insert_one(data)
    content_id = content.inserted_id

    logger.info(f"content_id : {content_id}")
    logger.info(f"content : {db.find_one({'_id': ObjectId(content_id)})}")
   
    return {"programs_id":'content_id' }

# 프로그램 수정
@router.put("/programs/posts/{id}", tags=['programs'])
def update_program_post( id: str, programs: Programs, token: str = Header()):

    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    logger.info(f"payload : {payload}")

    if 'email' in payload:
        email = payload['email']
    else:
        email = payload['sub']
    
    if email != 'admin@gmail.com': # 관리자만 작성할 수 있음. 
        logger.error("wrong admin email")
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

    logger.info(f"db : {db}")
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

            logger.info(f"content : {db.find_one({'_id': ObjectId(id)})}")

            content = db.find_one({"_id": ObjectId(id)})

            return {"update_program_post_id": id}
    except IndexError:
        logger.error("no matched content id")
        raise HTTPException(status_code=404, detail="Post not found")
    
# 프로그램 삭제
@router.delete("/programs/posts/{id}", tags=['programs'])
async def delete_program_post(id: str, token: str = Header()):
    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    logger.info(f"payload : {payload}")

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
        if db.count_documents({'$and': {"_id": ObjectId(id)}}) > 0:

            db.delete_one({"_id": ObjectId(id)})
            return {"deleted_program_id ": id}
        
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
        'program_post_id': 'Referred  program_post_id',
        'content': 'comment maximum 300 letters'}

# 댓글 추가
@router.post("/comments/posts", tags=['comments'])
def create_comment(comments: Comments, token: str = Header()):
    logger.info(f"comments : {comments}")
    logger.info(len(comments.content)) # pydantic이 최대 글자수를 넘는 순간 에러를 발생시킨다.

    # if len(comments.content) > 300:
    #     raise HTTPException(status_code=400, detail='Maximum 300 letters')

    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    except:
        logger.error('token is invalid')
        raise HTTPException(status_code=401, detail='Invalid token')

    logger.info(f"payload : {payload}")

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
        "created_at" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    content = db.insert_one(data)

    content_id = content.inserted_id

    logger.info(f"content_id : {content_id}")
    logger.info(f"content : {db.find_one({'_id': ObjectId(content_id)})}")

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
        logger.info(f"content{j}: ", i)

    logger.info(f"List : {return_list}")
    json_list = json.loads(json_util.dumps(return_list))
    logger.info(f"Json List : {json_list}")

    return json_list

# 댓글 수정
@router.put("/comments/posts/{id}", tags=['comments'])
def update_comment_post(id: str, comments: Comments, token: str = Header()):

    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    logger.info(f"payload : {payload}")

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
            logger.info(f"content : {content}")

            return {"update_program_post_id": id}

    except IndexError:
        logger.info("no matched content_id")
        raise HTTPException(status_code=404, detail="Post not found")

# 댓글 삭제
@router.delete("/comments/posts/{id}", tags=['comments'])
async def delete_post(id: str, token: str = Header()):
    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    logger.info(f"payload : {payload}")

    if 'email' in payload:
        email = payload['email']
    else:
        email = payload['sub']
    
    admin_list = ['admin@gmail.com']
    if not email in admin_list :
        raise HTTPException(status_code=401, detail='Only admin accounts are permitted')

    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["program_db"]
    
    try:
        if db.count_documents({'$and': {"_id": ObjectId(id)}}) > 0:

            db.delete_one({"_id": ObjectId(id)})
            return {f"content_id : {id} ": "delete successed"}
        raise HTTPException(status_code=404, detail="Comment not found")
        
    except IndexError:
        raise HTTPException(status_code=404, detail="Comment not found")

# 좋아요 
