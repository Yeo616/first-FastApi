from passlib.hash import pbkdf2_sha256
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta
from typing import Union, Any
from jose import JWTError, jwt
import pymongo

# openssl로 생성한 secret_key
SECRET_KEY = 'adcec27a3417b2de82130a2c54fc5c65aca0d7fa41b0a01dc310f3c78a62f885'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

password_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

# 일반 암호를 사용하여 DB에 안전하게 저장할 수 있는 해시를 반환
def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

# 일반 암호와 해시된 암호를 사용하고 암호가 일치하는지 여부를 나타냄
def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)

# === MongoDB 연결
# DB연결
async def connect_mongodb() -> dict:
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_test = myclient["test"] # Local의 Test DB 접근
    db = db_test["user_db"] # user_db Collection 생성 및 접근
    return db


# =============예전 프로젝트에서 사용했던 방법

# 원문 비밀번호를, 암호화 하는 함수
def hash_password(password) :
    # 공개되면 안되는 salt
    # TODO 이보다 더 좋은 보안책이 있었던 것 같다.
    
    salt = 'bs***123123'
    password = password + salt
    return pbkdf2_sha256.hash(password)

# 비밀번호가 맞는지 확인하는 함수
# password : 유저가 로그인할때 입력한 비빌번호
# hashed : DB에 저장되어있는, 암호화된 비밀번호
def check_password(password, hashed) :
    salt = 'bs***123123'
    return pbkdf2_sha256.verify(password+salt, hashed)