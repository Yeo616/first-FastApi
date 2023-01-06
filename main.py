from fastapi import FastAPI, Body,APIRouter, HTTPException, Depends, Request
from routers import check_login, register, login, kakao_login, naver_login, programs, story_images, story_CRUD,google_login, check_login
from fastapi.middleware.cors import CORSMiddleware
from Payment import iamport

from starlette.responses import FileResponse

app = FastAPI()

app.include_router(register.router)
app.include_router(login.router)
app.include_router(kakao_login.router)
app.include_router(naver_login.router)
app.include_router(google_login.router)
app.include_router(story_CRUD.router)
app.include_router(story_images.router)
app.include_router(iamport.router)
app.include_router(programs.router)
app.include_router(check_login.router)


# CORS: 허용 origin
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def g_index():
    return FileResponse('g_index.html')

# @app.get('/')
# async def test_get():
#     # client_host = request.client.host
#     return {"hello": "world"}

@app.post('/')
def test_post(txt:str):
    return {f"{txt} has tested."}


# ============ 로그 관련 =============
import logging
import traceback
from mongo_log import MongoHandler #// 직접 만든 Mongo 핸들러

logger   = logging.getLogger('uesr_log')   # logging 인스턴스 생성
level = logging.DEBUG                   # logger의 가장 낮은 수준인 DEBUG로 설정     
# 만일 가장 낮은 수준으로 level을 설정하지 않는다면, 
# 아래 handler들에서 setLevel을 한 것이 무의미해진다 (handler 별로 다른 level 설정하기)              
logger.setLevel(level)                     # logger에 level 부여하기 

#// Mongo 접속 정보 
host          = 'localhost'
port          = 27017
username      = None
password      = None
authMechanism = 'DEFAULT'

#// Mongo 데이터베이스 컬렉션 정보
databaseName     = 'test'
collectionName   = 'log_db'
capped           = False
size             = 100000
isCollectionDrop = False    #// Log Collection이 존재한다면 삭제하고, 재 생성(True)

#// Mongo 로깅 핸들러를 만든다
# 핸들러란 내가 로깅한 정보가 출력되는 위치를 설정
# handler object는 log 메세지의 level에 따라 적절한 log 메시지를 지정된 위치에 전달(dispatch)하는 역할 수행
mongoHandler = MongoHandler(host=host, port=port, username=username, password=password, authMechanism=authMechanism,
                            databaseName=databaseName, collectionName=collectionName, capped=capped, size=size,
                            isCollectionDrop=isCollectionDrop)
logger.addHandler(mongoHandler)    # logger는 addHander 메서드를 통해 handler 추가

def myfunc():
    try:
        5/0
    except Exception as e:
        logger.debug(traceback.format_exc())
        # traceback은 프로그램 실행 중 발생한 오류를 추적하고자 할 때 사용하는 모듈
        # traceback 모듈의 format_exc() 함수는 오류 추적 결과를 문자열로 반환해 주는 함수

# myfunc() # 로그 실행

# def main():
#     myfunc()
    
# if __name__ == '__main__':
#     main()
