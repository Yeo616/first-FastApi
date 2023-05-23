from fastapi import APIRouter, HTTPException, Header, Query, File, UploadFile, Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import  BaseModel, Field
# from pyjwt import decode, InvalidTokenError
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
# from jose import JWTError, jwt
import jwt
import logging
import pymongo
from bson import json_util
from bson.objectid import ObjectId

from fastapi.responses import FileResponse
import os
from typing import List
import uuid

import json
from typing import List
import pydantic
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str
import math

router = APIRouter(prefix='/story')

logger = logging.getLogger('story_CRUD')                                               # Logger 인스턴스 생성, 命名
logger.setLevel(logging.DEBUG)                                                       # Logger 출력 기준
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')# Formatter 생성, log 출력 형식

# log 출력
StreamHandler = logging.StreamHandler()                                              # 콘솔 출력 핸들러 생성
StreamHandler.setFormatter(formatter)                                                
logger.addHandler(StreamHandler)      

# UPLOAD_DIRECTORY = "./saving_images/"

class StoryPost(BaseModel): # 스키마 모델링
    program_title : str = Form() # essential, 연관된 프로그램 제목

    title:str = Form() # essential, 스토리 제목
    content:str = Form() # essential, 스토리 내용
    degree: str = Form() # essential, 회원 등급
    on_offline: str = Form() # essential, 수업 방식
    class_contents: str = Form() # essential, 수업 내용
    advance : str = Form() # essential, 기존 조건

    img: str | None = None # non-essential, 스토리 삽입 대표 이미지
    img_db_id: str | None = None # non-essential, 스토리 삽입 이미지

    author: str = Form() # essential, 작성자 email

    created_at: datetime = datetime.now() # essential, 스토리 생성 날짜
    updated_at: datetime| None = None # non-essential, 스토리 수정 날짜

    class config:
        schema_extra = {
        "program_title": "test1",
        "title":"title",
        "content":"write from here",
        "degree": "nobase",
        "on_offline": "online",
        "class_contents": "reading",
        "advance" : "quality",
        "author": "your email",
        "created_at" : datetime.now()}

class Degree(str): ## 회원 등급
    nobase: str = Form()
    elementary: str = Form()
    middle: str = Form()
    high: str = Form()
    university: str = Form()

class on_offline(str): ## 수업 방식
    online: str = Form()
    offline: str = Form()
    on_offline: str = Form()
    visit: str = Form()
    outside: str = Form()

class Class_contents(str): ## 수업 내용
    phonics: str = Form()
    reading: str = Form()
    toeic_ielts: str = Form()
    business_english: str = Form()
    job_interview: str = Form()
    etc: str = Form()

class Advance(str): ## 기존 조건
    quality:str = Form()
    facilities:str = Form()
    price : str = Form()
    environment  : str = Form()
    system : str = Form()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')

JWT_SECRET = 'adcec27a3417b2de82130a2c54fc5c65aca0d7fa41b0a01dc310f3c78a62f885'
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 선택/옵션으로 검색기능, (토큰x, 페이징 처리)
@router.get("/search_option", tags=["story_without_Token"])
async def search_story(
                        search_option_degree:Degree = None, 
                        search_option_on_offline:on_offline = None,
                        search_option_class_contents:Class_contents = None,
                        search_option_class_advance:Advance = None,
                        page: int = Query(1, description="Page number", ge=1)
                        ):

    logger.info(f'first 2 datas : {search_option_degree}, {search_option_on_offline}')
    logger.info(f'last 2 datas : {search_option_class_contents}, {search_option_class_advance}')

    # 페이징: 한 페이지 당 몇 개의 게시물을 출력할 것인가
    limit = 10
 
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["story_db"]

    logger.info('db is connected')

    # 입력값이 없을 경우: 모든 데이터 출력
    if search_option_degree is None and search_option_on_offline is None and search_option_class_contents is None and search_option_class_advance is None:
        
        # datas = db.find({}) # 페이징 처리 안할 때
        datas = db.find({}).sort('created_at',-1).skip((page - 1) * limit).limit(limit) # 페이징 처리

        logger.info('no input data, return all the data')
        
        datas = list(datas)

        logger.info(f'data : {datas}')

        return datas  # story_db 컬렉션에 있는 모든 데이터를 가져옴

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

# read all story posts with token (which all author wrote)
@router.get("/posts/token", tags=['story']) 
def read_all_posts( token: str = Header(), 
                    page: int = Query(1, description="Page number", ge=1)):  
    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    except:
        logger.error("token is invalid")
        raise HTTPException(status_code=401, detail='Invalid token')

    logger.info(f"payload : {payload}")

    if 'email' in payload:
        author = payload['email']
    else:
        author = payload['sub']

    # 페이징: 한 페이지 당 몇 개의 게시물을 출력할 것인가
    limit = 10

    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["story_db"]

    # TODO: decoded token and the author info are needed
    # content = db.find({},{"author": "decoded token"})
    content = db.find({"author": author}).sort('created_at',-1)
    content = list(content)

    # 결과값이 없으면
    if len(content) <= 0:
        return {"results": "No data found"}
   
    # limit(한 페이지에 보여주는 결과) 보다 결과값이 적으면, 페이징 처리할 필요가 없음
    if len(content) <= limit:
        return content
    else:
        content = db.find({"author": author}).sort('created_at',-1).skip((page - 1) * limit).limit(limit)
        content = list(content)
       
    # limit보다 결과물이 많을 때
    # 페이징: 게시물의 총 개수 세기
    tot_count = len(list(db.find({"author": author})))
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
    return content

    # return_list = []
    # j=0
    # for i in content:
    #     return_list.append(i)
    #     j+=1
    #     logger.info(f"content{j}: ", i)

    # logger.info(f"List : {return_list}")
    # json_list = json.loads(json_util.dumps(return_list))
    # logger.info(f"Json List : {json_list}")
    # return json_list

def validate_token(token: str):
    try:
        decoded_info = jwt.decode(f'Bearer {token}', JWT_SECRET , [JWT_ALGORITHM])
        logger.info(decoded_info['sub'])
        return decoded_info
    except:
        logger.error(f"token : {token} is not valid")
        raise HTTPException(status_code=401, detail= 'Invalid token')

# 하나의 스토리 읽기(토큰x)
@router.get('/posts/{id}')
async def read_single_post(id: str):
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["story_db"]

    try:
        content = db.find_one({"_id": ObjectId(id)})
        logger.info(f"content : {content}")
        return content

    except IndexError:
        raise HTTPException(status_code=404, detail="wrong story_id")    

# 하나의 스토리 읽기(토큰o) -> 비공개 게시물 등
@router.get('/posts/token/{id}')
async def read_single_post_token(id: str, token: str = Header()):
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["story_db"]

    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    logger.info(f"payload : {payload}")

    if 'email' in payload:
        author = payload['email']
    else:
        author = payload['sub']

    try:
        content = db.find_one({'$and': [{"_id": ObjectId(id)},{'author': author}]})
        logger.info(f"content : {content}")
        return content

    except IndexError:
        raise HTTPException(status_code=400, detail="Post not found")


# 스토리 추가(with file), 토큰없이 테스트
@router.post("/posts/test", tags=['story_without_Token'])
async def create_post_test(
                        # post: StoryPost = Form(...),
                        # program_title : str , 
                        # title:str , 
                        # content:str , 
                        # degree: str , 
                        # on_offline: str , 
                        # class_contents: str , 
                        # advance : str , 
                        program_title : str = Form(...), 
                        title:str = Form(...), 
                        content:str = Form(...), 
                        degree: str = Form(...), 
                        on_offline: str = Form(...), 
                        class_contents: str = Form(...), 
                        advance : str = Form(...), 
                        files: UploadFile = File(default=None)
                     ):
    # logger.info(f"had input : {post}")
    logger.info(f"had input : program title: {program_title}, title : {title}, content : {content}, degree: {degree}, on_offline : {on_offline}, class_contents : {class_contents}, advance: {advance}")
    logger.info(f"files : {files}")

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
   
    #프로그램 관련 DB 연결
    program_db = myclient['test']['program_db']
    # program_title = post.program_title
    
    # 입력받은 값: program_title
    program_info_db = program_db.find({"program_title": program_title})
    program_info_db = list(program_info_db)
    logger.info(f"program_title_db : {program_info_db}")
    logger.info(f"len(program_title_db) : {len(program_info_db)}")

    # program_title 입력이 잘못 되었을 경우
    if len(program_info_db) != 1:
        raise HTTPException(status_code=400, detail="wrong program title") 
    # logger.info(f'program_title_count : {program_db.count_documents({"program_title": post.program_title})}')
    logger.info(f'program_title_count : {program_db.count_documents({"program_title": program_title})}')

    # 참고하는 프로그램 정보
    program_id = program_info_db[0]['_id']
    logger.info(f"program_title_db_id : {program_id}")

    # DB연결
    db = myclient["test"]["story_db"]
    
    data = {"program_title": program_title,
            "program_id": program_id,
            "title": title, 
            "content": content, 
            "degree": degree,
            "on_offline": on_offline,
            "class_contents": class_contents,
            "advance" : advance,
            "author": "test",
            "created_at": datetime.now()}

    content = db.insert_one(data)
    # logger.info(f"content : {content}")
    content_id = content.inserted_id
    logger.info(f"this content_id : {content_id}")

    # 생성한 content_id
    data_in_db = db.find_one({"_id": ObjectId(content_id)})
    logger.info(f"content : {data_in_db}")
    
    if files is None:
        return {"content_id":f"{content_id}", # 스토리 콘텐츠 아이디
                "content_data": data_in_db,   # 스토리 입력 값
                "program_info":f"{program_info_db}"} # 연관된 프로그램 정보
    
    ##============ 이미지 업로드(대표 이미지) ==================
    # 이미지 저장할 경로 지정
    UPLOAD_DIRECTORY = "./saving_images/"
    LOCAL_URL = "http://192.168.1.101:8000"

    # 이미지 DB 연결
    image_db = myclient["test"]["image_db"]

    currentTime = datetime.now().strftime("%Y%m%d%H%M%S")
    
    contents = await files.read() # 파일을 읽는 동안 CPU가 다른 일을 하도록 명령
    saved_file_name = f"{currentTime}{str(uuid.uuid4())}.jpg" # 업로드한 시간과 UUID를 이용해서 유니크한 파일명으로 변경
    saved_file_path = f"{LOCAL_URL}/images/{saved_file_name}" # localhost:8000/ 파일 경로 url

    # DB에 이미지 저장
    image_data = {
            "story_refered_id" : ObjectId(content_id),
            "image_url": saved_file_path,
            "image_name": saved_file_name,
            "created_at": datetime.now()}

    image_content = image_db.insert_one(image_data)
    image_content_id = image_content.inserted_id
    logger.info(f"image content_id : {image_content_id}")

    # logger.info(f"original file name: {file.filename}")
    logger.info(f"file_names : {saved_file_name}")
    logger.info(f"file_path: {saved_file_path}")

    with open(os.path.join(UPLOAD_DIRECTORY, saved_file_name), "wb") as fp: # 해당 경로에 있는 파일을 바이러니 형식으로 open
        fp.write(contents) # 로컬에 이미지 저장(쓰기)
    
    # 위에 생성한 story에다가 img_url 추가하기
    db.update_one({"_id": ObjectId(content_id)},{"$set":{"img": saved_file_path, "img_db_id": ObjectId(image_content_id)}})

    logger.info(f"content_modified : {db.find_one({'_id': ObjectId(content_id)})}")
    
    content_db = db.find_one({"_id": ObjectId(content_id)})

    # 연관된 프로그램 정보도 넘기게 하였음.
    return {
            "file_path": saved_file_path, # 파일 더미에서 각 저장한 경로 및 파일명 호출
            "content_id":f"{content_id}", # 스토리 콘텐츠 아이디
            "content_data": content_db,   # 스토리 입력 값
            "program_info":f"{program_info_db}"
            } # 연관된 프로그램 정보

# create a new story post with token(with file)
@router.post("/posts", tags=['story'])
async def create_post(program_title : str = Form(...),
                title:str = Form(...),
                content:str = Form(...),
                degree: str = Form(...),
                on_offline: str = Form(...),
                class_contents: str = Form(...),
                advance : str = Form(...),
                files: UploadFile = File(default=None),
                token: str = Header()):
    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    logger.info(f"payload : {payload}")

    if 'email' in payload:
        author = payload['email']
    else:
        author = payload['sub']

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
   
    #프로그램 관련 DB 연결
    program_db = myclient['test']['program_db']
   
    # 입력받은 값: program_title
    program_info_db = program_db.find({"program_title": program_title})
    program_info_db = list(program_info_db)
    logger.info(f"program_title_db : {program_info_db}")
    logger.info(f"len(program_title_db) : {len(program_info_db)}")
 
    # program_title 입력이 잘못 되었을 경우
    if len(program_info_db) != 1:
        raise HTTPException(status_code=400, detail="wrong program title")
    logger.info(f'program_title_count : {program_db.count_documents({"program_title": program_title})}')
 
    # 참고하는 프로그램 정보
    program_id = program_info_db[0]['_id']
    logger.info(f"program_title_db_id : {program_id}")


    # DB연결
    db = myclient["test"]["story_db"]
   
    data = {"program_title": program_title,
            "program_id": program_id,
            "title": title,
            "content": content,
            "degree": degree,
            "on_offline": on_offline,
            "class_contents": class_contents,
            "advance" : advance,
            "author": author,
            "created_at": datetime.now()}

    content = db.insert_one(data)
    content_id = content.inserted_id
    logger.info(f"this content_id : {content_id}")

    # 생성한 content_id
    data_in_db = db.find_one({"_id": ObjectId(content_id)})
    logger.info(f"content : {data_in_db}")
   
    if files is None:
        return {"content_id":f"{content_id}", # 스토리 콘텐츠 아이디
                "content_data": data_in_db,   # 스토리 입력 값
                "program_info":f"{program_info_db}"} # 연관된 프로그램 정보
       
    ##============ 이미지 업로드(대표 이미지) ==================
    # 이미지 저장할 경로 지정
    UPLOAD_DIRECTORY = "./saving_images/"
    LOCAL_URL = "http://192.168.1.101:8000"
 
    # 이미지 DB 연결
    image_db = myclient["test"]["image_db"]
 
    currentTime = datetime.now().strftime("%Y%m%d%H%M%S")
   
    contents = await files.read() # 파일을 읽는 동안 CPU가 다른 일을 하도록 명령
    saved_file_name = f"{currentTime}{str(uuid.uuid4())}.jpg" # 업로드한 시간과 UUID를 이용해서 유니크한 파일명으로 변경
    saved_file_path = f"{LOCAL_URL}/images/{saved_file_name}" # localhost:8000/ 파일 경로 url
 
    # DB에 이미지 저장
    image_data = {
            "story_refered_id" : ObjectId(content_id),
            "image_url": saved_file_path,
            "image_name": saved_file_name,
            "created_at": datetime.now()}
 
    image_content = image_db.insert_one(image_data)
    image_content_id = image_content.inserted_id
    logger.info(f"image content_id : {image_content_id}")
 
    # logger.info(f"original file name: {file.filename}")
    logger.info(f"file_names : {saved_file_name}")
    logger.info(f"file_path: {saved_file_path}")
 
    with open(os.path.join(UPLOAD_DIRECTORY, saved_file_name), "wb") as fp: # 해당 경로에 있는 파일을 바이러니 형식으로 open
        fp.write(contents) # 로컬에 이미지 저장(쓰기)
   
    # 위에 생성한 story에다가 img_url 추가하기
    db.update_one({"_id": ObjectId(content_id)},{"$set":{"img": saved_file_path, "img_db_id": ObjectId(image_content_id)}})
 
    logger.info(f"content_modified : {db.find_one({'_id': ObjectId(content_id)})}")
   
    content_db = db.find_one({"_id": ObjectId(content_id)})
 
    # 연관된 프로그램 정보도 넘기게 하였음.
    return {
            "file_path": saved_file_path, # 파일 더미에서 각 저장한 경로 및 파일명 호출
            "content_id":f"{content_id}", # 스토리 콘텐츠 아이디
            "content_data": content_db,   # 스토리 입력 값
            "program_info":f"{program_info_db}"
            } # 연관된 프로그램 정보

# update a story post with token
@router.put("/posts/{id}", tags=['story'])
def update_post( id: str, post: StoryPost, token: str = Header()):
    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    logger.info(f"payload : {payload}")

    if 'email' in payload:
        author = payload['email']
    else:
        author = payload['sub']
    
        # 사전 유효성 검사
    degree_list = ["nobase", "elementary", "middle", "high", "university"]
    on_offline_list = ["online", "offline", "on_offline", "visit", "outside"]
    class_contents_list = ["phonics", "reading", "toeic_ielts", "business_english", "job_interview", "etc"]
    advance_list = ["quality", "facilities", "price", "environment", "system"]

    if not post.degree in degree_list:
        raise HTTPException(status_code=400, detail="wrong degree input")
   
    if not post.on_offline in on_offline_list:
        raise HTTPException(status_code=400, detail="wrong on_offline input")
   
    if not post.class_contents in class_contents_list:
        raise HTTPException(status_code=400, detail="wrong class_contents input")

    if not post.advance in advance_list:
        raise HTTPException(status_code=400, detail="wrong advance input")
    
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
   
    #프로그램 관련 DB 연결
    program_db = myclient['test']['program_db']
    program_title = post.program_title
    # 입력받은 값: program_title
    program_info_db = program_db.find({"program_title": program_title})
    program_info_db = list(program_info_db)
    logger.info(f"program_title_db : {program_info_db}")
    logger.info(f"len(program_title_db) : {len(program_info_db)}")

    # program_title 입력이 잘못 되었을 경우
    if len(program_info_db) != 1:
        logger.info(f"program_title is wrong")
        raise HTTPException(status_code=400, detail="wrong program title") 
    
    logger.info(f'program_title_count : {program_db.count_documents({"program_title": post.program_title})}')

    # 참고하는 프로그램 정보
    program_id = program_info_db[0]['_id']
    logger.info(f"program_title_db_id : {program_id}")

    db = myclient["test"]["story_db"]
    logger.info(f"db : {db}")

    try:
        if db.count_documents({'$and': [{"_id": ObjectId(id)},{"author": author}]}) > 0:

            db.update_one({"_id": ObjectId(id)},
                        {"$set":{"program_title": post.program_title,
                                "program_id": program_id,
                                "title": post.title,
                                "content":post.content,
                                "degree": post.degree,
                                "on_offline": post.on_offline,
                                "class_contents": post.class_contents,
                                "advance" : post.advance,
                                },
                        "$currentDate": {"lastModified": True}})

            content = db.find_one({"_id": ObjectId(id)})
            logger.info(f"content : {content}")

            return content
    except IndexError:
        logger.info("no matched content_id")
        raise HTTPException(status_code=404, detail="Post not found")

# delete a story post with token
@router.delete("/posts/{id}", tags=['story'])
async def delete_post(id: str, token: str = Header()):
    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail='Invalid token')

    logger.info(f"payload : {payload}")

    if 'email' in payload:
        author = payload['email']
    else:
        author = payload['sub']
    
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient["test"]["story_db"]
    
    try:
        
        if db.count_documents({'$and': {"_id": ObjectId(id)}}) > 0:
            content_to_delete = db.find({"_id": ObjectId(id)}) 
            content_to_delete = list(content_to_delete)
            logger.info(f"content_to_delete : {content_to_delete}")
            story_author = content_to_delete[0]['author']

            # 작성자 혹은 또 다른 관리자만 삭제 가능
            if author == 'admin@gmail.com'or author == story_author :
                db.delete_one({"_id": ObjectId(id)})
                # print("content : ",content.raw_result)
                return {f"content_id : {id} ": "delete successed"}

        raise HTTPException(status_code=404, detail="Post not found")
        
    except IndexError:
        raise HTTPException(status_code=404, detail="Post not found")

# # 모든 스토리 보기 함수(토큰x, 페이징 입력 가능)
# @router.get("/readall/pagination",  tags=['story_without_Token'])
# def story_list( page: int = Query(1, description="Page number", ge=1), 
#                 limit = 3):
    
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     db = myclient["test"]["story_db"]

#     # 한 페이지 당 몇 개의 게시물을 출력할 것인가
#     # limit = 3

#     datas = db.find({}).sort('created_at',-1).skip((page - 1) * limit).limit(limit)  # story_db 컬렉션에 있는 모든 데이터를 가져옴

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
