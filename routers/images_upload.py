from fastapi import APIRouter, UploadFile, File
from datetime import datetime
from fastapi.responses import FileResponse
from datetime import datetime
from typing import List

import uuid
import os

router = APIRouter(prefix='/images')

# 이미지 로컬에 업로드
@router.post("/uploadfiles")
async def create_upload_files(files: List[UploadFile] = File(...)):
    
    # 이미지 저장할 경로 지정
    UPLOAD_DIRECTORY = "./"

    currentTime = datetime.now().strftime("%Y%m%d%H%M%S")
    for file in files:
        contents = await file.read() # 파일을 읽는 동안 CPU가 다른 일을 하도록 명령
        saved_file_name = f"{currentTime}{str(uuid.uuid4())}.jpg" # 업로드한 시간과 UUID를 이용해서 유니크한 파일명으로 변경
         
        with open(os.path.join(UPLOAD_DIRECTORY, saved_file_name), "wb") as fp: # 해당 경로에 있는 파일을 바이러니 형식으로 open
            fp.write(contents) # 로컬에 이미지 저장(쓰기)

        print("original file name: ",file.filename)
        print("file_names : ",saved_file_name)

    return {"filenames": [saved_file_name for file in files]} # 파일 더미에서 각 저장한 파일명 호출

# 이미지 로컬에 있는 이미지 불러오기
@router.get('/{file_name}')
def get_image(file_name:str):
    return FileResponse(f"{os.getcwd()}/{file_name}") # os.getcwd: 현재 위치해있는 디렉토리를 표시

