from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta
import pymongo
from pydantic import BaseModel

# 비밀번호 암호화, 체크하는 함수
from utils import get_hashed_password, verify_password
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(prefix = '/users/snstype/email',tags= ['users'])

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

# 토큰 생성 함수
def create_access_token(data:dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    print("payload/data : ",to_encode)

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, JWT_ALGORITHM)

    print("encoded_jwt : ",encoded_jwt)

    return encoded_jwt

# Dependency Update
async def get_current_user(token:str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_AUTHORIZATION,
                                         detail="Coule not validate credentials",
                                         headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(f'Bearer {token}', JWT_SECRET , [JWT_ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = TokenData(username = username)
    except JWTError:
        raise credentials_exception
    
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_test = myclient["test"] # Local의 Test DB 접근
    db = db_test["user_db"] # user_db Collection 생성 및 접근

    email = token_data.username
    user = db.find_one({"email":email})
    # user = get_user(db, username = token_data.username)
    if user is None or db.count_documents({"email":email}) == 0:
        raise credentials_exception
    return user

from models.users import LoginModel

# Update the /token path operation

def authenticate_user(ba,username:str, password:str):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_test = myclient["test"] # Local의 Test DB 접근
    db = db_test["user_db"] # user_db Collection 생성 및 접근

    email = username
    user = db.find_one({"email":email})
    if db.count_documents({"email":email}) == 0:
        return False
    if not verify_password(password, user['hashed_password']):
        return False
    return user


@router.post('/token', response_model=Token)
async def login_for_access_token(form_data:OAuth2PasswordRequestForm=Depends()):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_test = myclient["test"] # Local의 Test DB 접근
    db = db_test["user_db"] # user_db Collection 생성 및 접근
    
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub":user['email']}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


# 일반 로그인
@router.post('/login', response_model=Token)
def UserLogin(user : LoginModel):
    # DB연결
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db_test = myclient["test"] # Local의 Test DB 접근
    db = db_test["user_db"] # user_db Collection 생성 및 접근

    email = user.email
    password = user.password

    print(email, password)
    print(2)

# 1. 클라이언트로부터 body로 넘어온 데이터를 받아온다: email, password

# # 1.1 이메일 형식이 맞는지 확인한다. -> Pydantic의 EmailStr이 우선 처리한다.
#     if not validate_email(email):
#         print(2.1)
#         raise HTTPException(status_code=400,detail="Email is not valid")
    
#     print(3)

# 2. 이메일로, DB에 이 이메일과 일치하는 데이터를 가져온다.

    if db.count_documents({"email":f"{email}"}) != 1:
        print(3.1)
        raise HTTPException(status_code=404, detail="User not found, please register first")
        
# 3. 해당 email로 찾은 행의 갯수가 1개이면, 유저 데이터를 정상적으로 받아온 것이고,
# 행의 갯수가 0이면, 요청한 이메일은 회원가입이 되어있지 않은 이메일이다.
    user_info = db.find_one({"email":f"{email}"})

    print(4)

# 4. 비밀번호가 맞는지 확인한다. 
# data['password'] 와 user_info['password']를 비교
    check = verify_password(password, user_info['hashed_password'])

    print(5)
    
    if check == False:
        print(4.1)
        raise HTTPException(status_code=400,detail="Password is incorrect")
        
    print(6)

# TODO 성공했으면 token 발행
    # data = {"email":f"{email}", "exp":f"{jwt_exp}"}
    data = {"email":f"{email}"}
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    print(7)
    try:
        access_token = create_access_token(data, expires_delta=access_token_expires)
    except Exception as e:
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail= str(e))

    # return {"access_token": access_token, 

    # access_token = jwt.encode(data, JWT_SECRET, algorithm = JWT_ALGORITHM)
    
    print("access_token: ",access_token)
    print(8)

    # response.headers["token"] = access_token
    # TODO token 발행 다른 방법도 있음. 
    return {"access_token": access_token, "token_type": "bearer"}
