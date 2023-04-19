from fastapi import APIRouter, HTTPException, Header, Query, File, UploadFile, Form
from pydantic import  BaseModel, Field
from datetime import datetime
import logging
import pymongo
from bson.objectid import ObjectId
from fastapi.responses import FileResponse
import pydantic
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

router = APIRouter(prefix='/statement-test', tags= ['test'])

logger = logging.getLogger('statement-test')                                               # Logger 인스턴스 생성, 命名
logger.setLevel(logging.DEBUG)                                                       # Logger 출력 기준
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')# Formatter 생성, log 출력 형식

# log 출력
StreamHandler = logging.StreamHandler()                                              # 콘솔 출력 핸들러 생성
StreamHandler.setFormatter(formatter)                                                
logger.addHandler(StreamHandler)      

# UPLOAD_DIRECTORY = "./saving_images/"

##############테스트 용도
class Data(BaseModel):
    text: str

@router.get('/')
async def save_text():
    myclient = pymongo.MongoClient()
    db = myclient["test"]["test_db"]
    logger.info('alarm : conneted')

    try:
        # Add the code that saves the text here
        docs = list(db.find({}).sort("created_at",-1))
        result_list =[]
        for doc in docs:
            logger.info(f"doc: {doc}")
            result_list.append(doc)
        return {"result": result_list}
                
    except Exception as e:
        # Log the error message to the server logs
        logger.info(f"Error saving text: {e}")
        # Return a 500 Internal Server Error response
        raise HTTPException(status_code=500, detail="Error saving text")

@router.post('/post')
async def save_text(text: Data):
    myclient = pymongo.MongoClient()
    logger.info(f"content_id : {text}")
    try:
        # Add the code that saves the text here
        db = myclient["test"]["test_db"]
        data = { 
            "text": text.text,
            "created_at": datetime.now()}
        db.insert_one(data)
        return {"text": text.text}
                
    except Exception as e:
        # Log the error message to the server logs
        logger.info(f"Error saving text: {e}")
        # Return a 500 Internal Server Error response
        raise HTTPException(status_code=500, detail="Error saving text")
