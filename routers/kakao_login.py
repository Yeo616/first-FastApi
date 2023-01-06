
from pydantic import BaseModel, EmailStr, Field
from fastapi import FastAPI, APIRouter, Body
from fastapi.responses import PlainTextResponse,JSONResponse
import pymongo
from datetime import datetime, timedelta
import jwt


router = APIRouter(prefix = '/users', tags= ['Social_login'])

class KakaoUser(BaseModel):
    sns_type = "kakao"
    email : EmailStr # 사용자 이메일
    username : str | None = None # 사용자 닉네임

class Token(BaseModel): # 토큰
    Authorization: str = None

class UserToken(BaseModel): # 유저 토큰
    username: str = None
    email: str = None
    nickname: str = None
    sns_type: str = None

# 추후에 AWS의 Secret Manager을 이용해 JWT_SECRET을 동적으로 가져오게 할 수 있다.
JWT_SECRET = 'adcec27a3417b2de82130a2c54fc5c65aca0d7fa41b0a01dc310f3c78a62f885'
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(*, data: dict = None, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(days=expires_delta)})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# request: 유저정보(email, nickname), response: 토큰만료기한, jwt token
# 받는 정보: (essential) 닉네임, 이메일/ (non-essential)프로필 사진, 연령대
@router.post('/snstype/kakao', description = "카카오 회원가입/로그인",response_class = JSONResponse)
def kakao_register( req = Body()):    

    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_test = myclient["test"] 
    db = db_test["user_db"] 

    email = req["email"]
    jwt_exp = req["expires"]
    
    print(email)
    print(db.find({"email":f"{email}"}))

    # DB에 데이터가 없다면, 회원가입
    if db.count_documents({"email":f"{email}"}) != 1:
        data = ({
        "register_method":"kakao",
        # "nickname": req.nickname,
        "email":f"{email}", 
        "created_at" : datetime.utcnow()
        })
        
        print(1.0)

        result = db.insert_one(data)
        print(2)
        print(result.inserted_id)

    print(3)
    # DB에 존재하는 사용자는 데이터를 가져온다. 

    user = db.find_one({"email":f"{email}"})
    data = {"email" : user['email'], "exp" : f"{jwt_exp}"}
    
    print(user)

    # 토큰을 만료기간까지 포함해서 발급한다.
    # 토큰 발행
    token = dict(
    # Authorization=f"Bearer {create_access_token(data=UserToken.from_orm.dict(user),)}")
    Authorization=f"Bearer {create_access_token(data=data,expires_delta=30)}")

    print(token)

    return req,token