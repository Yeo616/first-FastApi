from fastapi import APIRouter, HTTPException, Depends, status, Request, Header
from datetime import datetime, timedelta
import pymongo
from pydantic import BaseModel

# 비밀번호 암호화, 체크하는 함수
from utils import get_hashed_password, verify_password
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import pydantic
from bson import json_util
from bson.objectid import ObjectId
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str
import logging
import typing

router = APIRouter(prefix = '/users', tags= ['users'])

# 로그 생성
logger = logging.getLogger('check_login')                                               # Logger 인스턴스 생성, 命名
logger.setLevel(logging.DEBUG)                                                       # Logger 출력 기준 설정
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')# Formatter 생성, log 출력 형식

# log 출력
StreamHandler = logging.StreamHandler()                                              # 콘솔 출력 핸들러 생성
StreamHandler.setFormatter(formatter)                                                
logger.addHandler(StreamHandler)     

JWT_SECRET = 'adcec27a3417b2de82130a2c54fc5c65aca0d7fa41b0a01dc310f3c78a62f885'
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

jwt_exp = datetime.utcnow() + timedelta(days=30)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class Token(BaseModel): # endpoint에서 응답으로 사용될 token
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username:str | None = None

@router.get('/check-login')
async def check_login(token: Request = Header()): 
    
    logger.info(f"Header : {token}")
    logger.info(f"req.headers : {token.headers}")
    logger.info(f"req.headers.get('access_token') : {token.headers.get('access_token')}")

    token = token.headers.get('access_token')

    try :
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        logger.info(f"decoded_info : {payload}")
        logger.info(f"email : {payload['email']}")

        email = payload['email']
        
        # DB연결
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        db_test = myclient["test"]
        db = db_test["user_db"]

        # DB에 존재하는 사용자는 데이터를 가져온다.
        user = db.find_one({"email":f"{email}"})
        logger.info(f"user : {user}")
        logger.info(f"user['nickname'] : {user['nickname']}")

        nickname = user["nickname"]

        return {"email":email,"nickname":nickname}

    except:
        raise HTTPException(status_code=401, detail='Invalid token')
    
# 새로고침 할 때마다, 토큰을 받아서, 디코딩 한 다음에 이 사람이 로그인 상태인지 확인하는 것.
# refresh token 아직
