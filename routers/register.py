# from fastapi import APIRouter, HTTPException
# from email_validator import validate_email, EmailNotValidError
# from datetime import datetime
# import pymongo

# # User 입력값 형식 import
# from models.users import User_Register

# # 비밀번호 암호화, 체크하는 함수
# from utils import  get_hashed_password

# router = APIRouter(prefix = '/users/snstype/email',tags= ['users'])

# # 회원가입
# @router.post("/register")
# def user_register(user: User_Register): # 1. 클라에서 보내준 데이터 받기 + , program: Program

#     print("user for register info: ", user)
#     # DB연결
#     myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#     db_test = myclient["test"] # Local의 Test DB 접근
#     db = db_test["user_db"] # user_db Collection 생성 및 접근
    
#     # 2. 이메일 주소 형식이 제대로 된 주소 형식인지 확인
#     try:
#         validate_email(user.email)
#         print(0)
    
#     except EmailNotValidError as e:
#         print(0.1)
#         return {"error": f"{e}" }

#     # 2-1. 이미 DB에 존재하고 있는 이메일인지 체크한다.
#     if db.count_documents({"email":f"{user.email}"}) > 0:
#         print(0.2)
#         raise HTTPException(detail="this email already exists", status_code = 400)
    
#     print(1)

#     # 3. 닉네임이 이미 DB에 있는지 체크한다. 
#     if db.count_documents({"nickname":f"{user.nickname}"}) >0:
#         print(1.1)
#         raise HTTPException(detail="this nickname already exists", status_code = 400)

#     # 4. 비밀번호의 길이가 유효한지 체크한다.
#     # 비번길이는 8자리 이상만!
#     print(2)

#     if len(user.password) < 8 :
#         raise HTTPException(detail="The field Password must be a string with a mininum length of 8.", status_code=400)

#     print(3)
#     # 4-1. 비밀번호 재 입력 후 맞는지 확인한다.
#     if user.password != user.password_confirm:
#         raise HTTPException(detail="the password do not match", status_code=400)

#     print(4)
#     # 5. 비밀번호를 암호화 한다. TODO: bcrypt
#     hashed_password = get_hashed_password(user.password)
#     print(5)
#     print("hashed_password: ",hashed_password)

#     # 6. DB에 회원정보를 저장한다.
#     data = ({
#             "register_method":"email",
#             "email":f"{user.email}", 
#             "nickname": user.nickname,
#             "hashed_password": hashed_password,
#             "status": user.status,
#             "created_at" : datetime.utcnow()
#             })
            
#     print(6)

#     result = db.insert_one(data)
#     print("db inserted_id: ",result.inserted_id)

#     print("register done")

#     return {"status": "succeed"}
