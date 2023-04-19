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

router = APIRouter(prefix='/inquiry')

logger = logging.getLogger('inquiry_CRUD')                                               # Logger 인스턴스 생성, 命名
logger.setLevel(logging.DEBUG)                                                       # Logger 출력 기준
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')# Formatter 생성, log 출력 형식

# log 출력
StreamHandler = logging.StreamHandler()                                              # 콘솔 출력 핸들러 생성
StreamHandler.setFormatter(formatter)                                                
logger.addHandler(StreamHandler)      

# UPLOAD_DIRECTORY = "./saving_images/"

##############테스트 용도
class Data(BaseModel):
    key: str
    text: str

@router.get('/test')
async def save_text():
    myclient = pymongo.MongoClient()
    db = myclient["test"]["inquiry_db"]
    print('alarm : conneted')

    try:
        # Add the code that saves the text here
        docs = list(db.find({}))
        result_list =[]
        for doc in docs:
            print(doc)
            result_list.append(doc)
        return {"result": result_list}
                
    except Exception as e:
        # Log the error message to the server logs
        print(f"Error saving text: {e}")
        # Return a 500 Internal Server Error response
        raise HTTPException(status_code=500, detail="Error saving text")

@router.post('/test')
async def save_text(example_data: Data):
    myclient = pymongo.MongoClient()
    print(example_data)
    try:
        # Add the code that saves the text here
        db = myclient["test"]["inquiry_db"]
        data = { 
            "test_data": example_data.key,
            "text": example_data.text,
            "created_at": datetime.now()}
        db.insert_one(data)
        return {"key value": example_data.key, 
                "text": example_data.text}
                
    except Exception as e:
        # Log the error message to the server logs
        print(f"Error saving text: {e}")
        # Return a 500 Internal Server Error response
        raise HTTPException(status_code=500, detail="Error saving text")

class InquiryPost(BaseModel): # 스키마 모델링
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

# 문의 추가(with file), 토큰없이 테스트
@router.post("/post/test", tags=['inquiry_without_Token'])
async def create_post_test(
                        selectedButton: str = Form(...), 
                        text:str = Form(...), 
                        secretCheck: bool = Form(...), 
                        files: UploadFile = File(default=None)
                     ):
    logger.info(f"button: {selectedButton}, text: {text}, text: {text}")
    # logger.info(f"files: {files}")

    if selectedButton is None: # 프론트에서도 처리함
        raise HTTPException(status_code=400, detail="Inquiry type is empty") 
    
    if text is None: # 프론트에서도 처리함
        raise HTTPException(status_code=400, detail="Inquiry text is empty") 

    # DB연결
    myclient = pymongo.MongoClient()
   
    # DB연결
    db = myclient["test"]["inquiry_db"]
    
    data = { "selectedButton": selectedButton,
            "inquiry_text": text, 
            "secretCheck" : secretCheck,
            "author": "test",
            "created_at": datetime.now()}
    # 사진은 나중에

    content = db.insert_one(data)
    content_id = content.inserted_id
    logger.info(f"this content_id : {content_id}")

    # 생성한 content_id
    data_in_db = db.find_one({"_id": ObjectId(content_id)})
    logger.info(f"content : {data_in_db}")
    
    if files is None:
        return {"content_id":f"{content_id}", # 스토리 콘텐츠 아이디
                "content_data": data_in_db}   # 스토리 입력 값
    
    # ##============ 이미지 업로드(대표 이미지) ==================
    # # 이미지 저장할 경로 지정
    # UPLOAD_DIRECTORY = "./saving_images/"
    # LOCAL_URL = "http://192.168.1.101:8000"

    # # 이미지 DB 연결
    # image_db = myclient["test"]["image_db"]

    # currentTime = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # contents = await files.read() # 파일을 읽는 동안 CPU가 다른 일을 하도록 명령
    # saved_file_name = f"{currentTime}{str(uuid.uuid4())}.jpg" # 업로드한 시간과 UUID를 이용해서 유니크한 파일명으로 변경
    # saved_file_path = f"{LOCAL_URL}/images/{saved_file_name}" # localhost:8000/ 파일 경로 url

    # # DB에 이미지 저장
    # image_data = {
    #         "story_refered_id" : ObjectId(content_id),
    #         "image_url": saved_file_path,
    #         "image_name": saved_file_name,
    #         "created_at": datetime.now()}

    # image_content = image_db.insert_one(image_data)
    # image_content_id = image_content.inserted_id
    # logger.info(f"image content_id : {image_content_id}")

    # # logger.info(f"original file name: {file.filename}")
    # logger.info(f"file_names : {saved_file_name}")
    # logger.info(f"file_path: {saved_file_path}")

    # with open(os.path.join(UPLOAD_DIRECTORY, saved_file_name), "wb") as fp: # 해당 경로에 있는 파일을 바이러니 형식으로 open
    #     fp.write(contents) # 로컬에 이미지 저장(쓰기)
    
    # # 위에 생성한 story에다가 img_url 추가하기
    # db.update_one({"_id": ObjectId(content_id)},{"$set":{"img": saved_file_path, "img_db_id": ObjectId(image_content_id)}})

    # logger.info(f"content_modified : {db.find_one({'_id': ObjectId(content_id)})}")
    
    # content_db = db.find_one({"_id": ObjectId(content_id)})

    # # 연관된 프로그램 정보도 넘기게 하였음.
    # return {
    #         "file_path": saved_file_path, # 파일 더미에서 각 저장한 경로 및 파일명 호출
    #         "content_id":f"{content_id}", # 스토리 콘텐츠 아이디
    #         "content_data": content_db,   # 스토리 입력 값
    #         "program_info":f"{program_info_db}"
    #         } # 연관된 프로그램 정보
