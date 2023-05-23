from typing import Generic, List, Optional, TypeVar, Union
from datetime import datetime
from pydantic import BaseModel, EmailStr
from enum import Enum


class UserModel(BaseModel): #
    
    register_method: str # 회원가입 방식: on_site / social
    register_social: Optional[str] = None # 소셜 회원가입 방식: Naver/ Kakao/ Google
    email: str
    password: str
    Password_confirm: str
    status:str
    nickname: str
    
    username: Optional[str] = None
    region: Optional[str] = None
    phone_number : Optional[str] = None
    profile_pic : Optional[str] = None
    created_at : datetime = None
    comment : Optional[str] = None

    class Config:
       schema_extra = {
            "example": {
                "nickname": "000",
                "email": "yeo@gmail.com",
                "status": "Junior",
                "password": "weakpassword",
                "Password_confirm": "weakpassword",
                "created_at" : datetime.utcnow()
            }}

class LoginModel(BaseModel):# 로그인에 필요한 양식
    email: EmailStr # essential
    password: str# essential

    class Config:
        schema_extra = {
            "example": {
                "email": "abdulazeez@x.com",
                "password": "weakpassword"
            }}

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

class SnsType(str, Enum):
    email: str = "email"
    naver: str = "naver"
    google: str = "google"
    kakao: str = "kakao"



class Log_Host(BaseModel): # 클라에서 데이터 보낼 때 양식
   
    _id : object # essential, 로그를 남기는 유저 -id
    name: str # essential , 로그를 남기는 유저 name
    ip_addr: str # essential, 로그를 남기는 유저 ip
    
class Log_Message(BaseModel): # 클라에서 데이터 보낼 때 양식
   
    time : datetime # essential, 로그를 남기는 시간
    host: object # essential # 이슈 발생 당사자
    message: str # essential , 해당 시간에 발생한 이슈
    
# class Password_confirmation(UserModel):
#     pass


# class program(BaseModel):
#          "program_title":"test",
#          "courses":{
#              "course_title":"test",
#              "price":1,
#              "student_amount":10 },
#          "start_date": "2022-11-29",
#          "end_date": "2023-11-29"
    # pass
