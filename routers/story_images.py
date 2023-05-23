from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import FileResponse
from datetime import datetime
import os
from typing import List
# from fastapi.staticfiles import StaticFiles
import logging
import uuid

router = APIRouter(prefix='/images', tags=['images'])

# @router.get("/")
# async def main():
#     return {"main": "Image Upload Directory"}

# @router.post("/files/")
# async def create_files(files: List[bytes] = File(...)):
#     return {"file_sizes": [len(file) for file in files]}

# 로그 생성
logger = logging.getLogger('story_images')                                               # Logger 인스턴스 생성, 命名
logger.setLevel(logging.DEBUG)                                                       # Logger 출력 기준 설정
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')# Formatter 생성, log 출력 형식

# log 출력
StreamHandler = logging.StreamHandler()                                              # 콘솔 출력 핸들러 생성
StreamHandler.setFormatter(formatter)                                                
logger.addHandler(StreamHandler)    


# 이미지 로컬에 업로드
@router.post("/uploadfiles")
async def create_upload_files(files: List[UploadFile] = File(...)):
    logger.info(files)
    # 이미지 저장할 경로 지정
    UPLOAD_DIRECTORY = "./saving_images/"
    LOCAL_URL = "http://localhost:8000"

    path_list = []

    currentTime = datetime.now().strftime("%Y%m%d%H%M%S")
    for file in files:
        contents = await file.read() # 파일을 읽는 동안 CPU가 다른 일을 하도록 명령
        saved_file_name = f"{currentTime}{str(uuid.uuid4())}.jpg" # 업로드한 시간과 UUID를 이용해서 유니크한 파일명으로 변경
        saved_file_path = f"{LOCAL_URL}/images/{saved_file_name}" # localhost:8000/ 파일 경로 url

        logger.info(f"original file name : {file.filename}")
        logger.info(f"file_names : {saved_file_name}")
        logger.info(f"file_path : {saved_file_path}")

        with open(os.path.join(UPLOAD_DIRECTORY, saved_file_name), "wb") as fp: # 해당 경로에 있는 파일을 바이러니 형식으로 open
            fp.write(contents) # 로컬에 이미지 저장(쓰기)
            path_list.append(saved_file_path)

    # return {"file_path": [saved_file_path for file in files], } # 파일 더미에서 각 저장한 경로 및 파일명 호출
    return {"file_path": [file for file in path_list], } # 파일 더미에서 각 저장한 경로 및 파일명 호출

UPLOAD_DIRECTORY = "./saving_images/"
# 이미지 로컬에 있는 이미지 불러오기
@router.get('/{file_name}')
def get_image(file_name:str):
    logger.info(f" getcwd: {os.getcwd()}")
    return FileResponse(f"{os.getcwd()}/{UPLOAD_DIRECTORY}/{file_name}") # os.getcwd: 현재 위치해있는 디렉토리를 표시



# ################### Image Upload.py에 있던 코드 하기 참고

# from fastapi import APIRouter, UploadFile, File, Form
# from datetime import datetime
# from fastapi.responses import FileResponse
# from datetime import datetime
# from typing import List

# import uuid
# import os
# import logging

# router = APIRouter(prefix='/images')

# # 로그 생성
# logger = logging.getLogger('images_upload')                                               # Logger 인스턴스 생성, 命名
# logger.setLevel(logging.DEBUG)                                                       # Logger 출력 기준 설정
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')# Formatter 생성, log 출력 형식

# # log 출력
# StreamHandler = logging.StreamHandler()                                              # 콘솔 출력 핸들러 생성
# StreamHandler.setFormatter(formatter)                                                
# logger.addHandler(StreamHandler)    



# # 이미지 로컬에 업로드
# @router.post("/uploadfiles")
# async def create_upload_files(files: List[UploadFile] = File(...)):
    
#     # 이미지 저장할 경로 지정
#     UPLOAD_DIRECTORY = "./"

#     currentTime = datetime.now().strftime("%Y%m%d%H%M%S")
#     for file in files:
#         contents = await file.read() # 파일을 읽는 동안 CPU가 다른 일을 하도록 명령
#         saved_file_name = f"{currentTime}{str(uuid.uuid4())}.jpg" # 업로드한 시간과 UUID를 이용해서 유니크한 파일명으로 변경
         
#         with open(os.path.join(UPLOAD_DIRECTORY, saved_file_name), "wb") as fp: # 해당 경로에 있는 파일을 바이러니 형식으로 open
#             fp.write(contents) # 로컬에 이미지 저장(쓰기)

#         logger.info(f"original file name : {file.filename}")
#         logger.info(f"file_names : {saved_file_name}")

#     return {"filenames": [saved_file_name for file in files]} # 파일 더미에서 각 저장한 파일명 호출

# # 이미지 로컬에 있는 이미지 불러오기
# @router.get('/{file_name}')
# def get_image(file_name:str):
#     return FileResponse(f"{os.getcwd()}/{file_name}") # os.getcwd: 현재 위치해있는 디렉토리를 표시



    
