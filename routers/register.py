from fastapi import APIRouter, HTTPException
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import pymongo

# # User 입력값 형식 import
# from models.users import User_Register

# 비밀번호 암호화, 체크하는 함수
from utils import  get_hashed_password
import logging
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix = '/users/snstype/email',tags= ['users'])

# 로그 생성
logger = logging.getLogger('register')                                               # Logger 인스턴스 생성, 命名
logger.setLevel(logging.DEBUG)                                                       # Logger 출력 기준
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')# Formatter 생성, log 출력 형식

# log 출력
StreamHandler = logging.StreamHandler()                                              # 콘솔 출력 핸들러 생성
StreamHandler.setFormatter(formatter)                                                
logger.addHandler(StreamHandler)       # logger 인스턴스에 handler 설정

class User(BaseModel): # 로그인에 필요한 양식
    email: EmailStr # essential
    password: str # essential

class User_Register(User): # 회원가입에 필요한 양식
    password_confirm: str # essential
    status:str # essential, Kinder/ Junior/ College / Adults,Senior
    nickname: str # essential

class UserInDB(User): # DB에 저장될 양식
    hashed_password: str # essential
    register_method: str # essential, 회원가입 방식: on_site / social
    register_social: Optional[str] = None # non-essential, 소셜 회원가입 방식: Naver/ Kakao/ Google
    created_at : datetime # essential

    username: str | None = None # non-essential
    region: Optional[str] = None # non-essential
    phone_number : Optional[str] = None # non-essential
    profile_pic : Optional[str] = None # non-essential
    reservated_programs: Optional[list] # non-essential, 프로그램 _id 리스트
    shopping_cart: Optional[list] = None # non-essential, 프로그램 _id 리스트
    updated_at: Optional[datetime] = None # non-essential
    comment : Optional[str] = None # non-essential

# 회원가입
@router.post("/register")
def user_register(user: User_Register): # 1. 클라에서 보내준 데이터 받기 + , program: Program
    
    logger.debug(f'user for register info: {user}')

    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_test = myclient["test"] # Local의 Test DB 접근
    db = db_test["user_db"] # user_db Collection 생성 및 접근
    
    # 2. 이메일 주소 형식이 제대로 된 주소 형식인지 확인
    try:
        validate_email(user.email)
        logger.info(f'user email: {user.email}')
    
    except EmailNotValidError as e:
        logger.error(f'email validator error')
        return {"error": f"{e}" }

    # 2-1. 이미 DB에 존재하고 있는 이메일인지 체크한다.
    if db.count_documents({"email":f"{user.email}"}) > 0:
        logger.error('email already exists')
        raise HTTPException(detail="this email already exists", status_code = 400)
    
    logger.info('email is available')

    # 3. 닉네임이 이미 DB에 있는지 체크한다. 
    if db.count_documents({"nickname":f"{user.nickname}"}) >0:
        logger.error('nickname already exists')
        raise HTTPException(detail="this nickname already exists", status_code = 400)

    # 4. 비밀번호의 길이가 유효한지 체크한다.
    # 비번길이는 8자리 이상만!
    logger.info('email and nickname are available')

    if len(user.password) < 8 :
        raise HTTPException(detail="The field Password must be a string with a mininum length of 8.", status_code=400)
   
    logger.info('length of password is passed')

    # 4-1. 비밀번호 재 입력 후 맞는지 확인한다.
    if user.password != user.password_confirm:
        raise HTTPException(detail="the password do not match", status_code=400)

    logger.info('password confirm is passed')

    # 5. 비밀번호를 암호화 한다. TODO: bcrypt
    hashed_password = get_hashed_password(user.password)
    logger.info(f'hashed_password : {hashed_password}')

    # 6. DB에 회원정보를 저장한다.
    data = ({
            "register_method":"email",
            "email":f"{user.email}", 
            "nickname": user.nickname,
            "hashed_password": hashed_password,
            "status": user.status,
            "created_at" : datetime.utcnow()
            })
            
    logger.info('data has made')

    result = db.insert_one(data)
    logger.info(f'db inserted_id: {result.inserted_id}')
 
    logger.info('register is done')

    return {"status": "succeed"}
