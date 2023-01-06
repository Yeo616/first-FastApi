# from fastapi import APIRouter,FastAPI, Request, Response, Header, HTTPException
# import pymongo
# from datetime import datetime
# import jwt
# import requests

# router = APIRouter(prefix='', tags=['payment'])

# JWT_SECRET = 'adcec27a3417b2de82130a2c54fc5c65aca0d7fa41b0a01dc310f3c78a62f885'
# JWT_ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# #결제번호, 주문번호 추출
# @router.post("/payments/complete")
# async def complete_payment(request: Request, response: Response, token:str = Header()):
#     # get request body and extract the 'imp_uid and merchant_uid values

#     # get token and get users_info

#     try :
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
#     except:
#         raise HTTPException(status_code=401, detail='Invaild token')

#     print("payload : ", payload)

#     if 'email' in payload:
#         email = payload['email']
#     else:
#         email = payload['sub']


#     try:
#         body = await request.json()
#         imp_uid = body['imp_uid'] # 결제번호
#         merchant_uid = body['merchant_uid'] # 주문번호

#             # DB연결
#         myclient = pymongo.MongoClient("mongodb://localhost:27017/")
#         db = myclient["test"]["story_db"]
        
#         data = {"email": email,
#                 "imp_uid":imp_uid, 
#                 "merchant_uid": merchant_uid,
#                 "created_at": datetime.now()}

#         content = db.insert_one(data)
#         print("content.inserted_id : ",content.inserted_id)

#     except Exception as e:
#         response.status_code = 400
#         return str(e)


# # # Token 발급(현진 토큰)
# # REST_API_KEY = "1278023411451275"
# # REST_API_SECRET = "o8Aq9VZspHiJUcZbzdEfIZDLe0R75baaVo6dezgwy76hCFEMsUb3VndtGYuJgK27OXKZt3hM8mnVvrH3"

# # Token 발급(현석 토큰)
# REST_API_KEY = "5560317432871444"
# REST_API_SECRET = "fYEqTzYabjudBlrrYo5Ct5fjMJANsNcFzaDf8AYPNJjRp1eGRlalbqhqThS1umqHJnLBMSccjuqa8dDA"

# def get_access_token():
#     response = requests.post("https://api.iamport.kr/users/getToken", 
#                 json={"imp_key": REST_API_KEY,
#                       "imp_secret": REST_API_SECRET},
#                 headers={ "Content-Type": "application/json" })

#     token_response = response.json()
#     access_token = token_response['response']['access_token']
#     print("token_response : ", token_response)
#     # {'code': 0,
#     # 'message': None,
#     # 'response': {'access_token': '3a6312479ff4844ee541c89a5392da8d2b2f4553',
#     # 'now': 1671697238,    # 아임포트 REST AOU 서버의 현재시간
#     # 'expired_at': 1671699038}}    # token의 만료 시간 (UNIX timestamp, KST 기준)
#     print("access_token : ", access_token)
#     # access_token : 3a6312479ff4844ee541c89a5392da8d2b2f4553

#     return access_token


# #결제 정보 조회 -> RESTAPI access token 필요
# @router.post("/payments/complete")
# async def complete_payment(request: Request, response:Response, token:str = Header()):
#     print(request.json())
#     try:
#         body = await request.json()
#         imp_uid = body['imp_uid'] # 결제번호
#         merchant_uid = body['merchant_uid'] # 주문번호

#         access_token = get_access_token() # access token 발급 받기

#         # 결제 정보 확인
#         payment_response = requests.get(f"https://api.iamport.kr/payments/{imp_uid}", headers={
#             "Authorization": access_token
#         })
#         payment_data = payment_response.json()['response'] # 조회한 결제 정보

#         #### 결제정보 검증 후 저장
#         # DB에서 결제되어야하는 금액 조회

#         myclient = pymongo.MongoClient()
#         db_test = myclient["test"] # Local의 Test DB 접근
#         ordersdb = db_test.Order # Order Collection 생성 및 접근
#         user_oder_db = db_test.user_oder_db 

#         # Get amount to be paid from database
#         order = ordersdb.find_one({"merchant_uid": payment_data['merchant_uid']})
#         amount_to_be_paid = order['amount']

#         amount = payment_data['amount']
#         status = payment_data['status']

#         if amount == amount_to_be_paid: # 결제 금액 일치, 결제된 금액 = 결제되어야 하는 금액
#             # Save payment data to database
#             await ordersdb.update_one({"merchant_uid": merchant_uid}, {"$set": payment_data})

#         # token에서 유저정보 받기
#         try :
#             payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
#         except:
#             raise HTTPException(status_code=401, detail='Invaild token')

#         print("payload : ", payload)

#         if 'email' in payload:
#             email = payload['email']
#         else:
#             email = payload['sub']


#         if status == "ready": # 가상계좌 발급
#                 # DB에 가상계좌 발급 정보 저장
#                 vbank_num = payment_data['vbank_num']
#                 vbank_date = payment_data['vbank_date']
#                 vbank_name = payment_data['vbank_name']

#                 await user_oder_db.update_one({"email": email}, {"$set": {vbank_num, vbank_date, vbank_name}})
               
#                 # 가상계좌 발급 안내 문자메시지 발송
#                 response.status_code = 200
#                 return {"status": "vbankIssued", "message": f"Virtual account issued successfully. Account info {vbank_num} {vbank_date} {vbank_name}"}
        
#         elif status == "paid": # 결제완료
#                 response.status_code = 200
#                 return {"status": "success", "message": "Payment successful"}
        
#         else: # 결제금액 불일치, 위/변조 된 결제
#             raise HTTPException(status_code=400, detail={"status": "forgery", "message": "위조된 결제시도"})
   
#     except Exception as e:
#         response.status_code = 400
#         return e
        
# # 결제 정보를 DB에 저장하는 이유
# # 결제를 완료한 고객이 주문내역 페이지에서 결제 내역을 확인할 수 있도록 결제 정보를 자체 DB에 저장해야 하고, 
# # 결제 정보가 바뀔 때 마다 (전액/부분 환불 등) 아임포트 API를 이용해 동기화 한다.

# # 웹훅(Webhook)을 이용하여 알림 설정하기(필수사항)
# @router.post("/iamport-webhook")
# async def iamport_webhook(request: Request, response:Response, token:str = Header()):
#     try:
#         body = await request.json()
#         imp_uid = body['imp_uid'] # 결제번호
#         merchant_uid = body['merchant_uid'] # 주문번호

#         access_token = get_access_token() # access token 발급 받기

#         # 결제 정보 확인
#         payment_response = requests.get(f"https://api.iamport.kr/payments/{imp_uid}", headers={
#             "Authorization": access_token
#         })
#         payment_data = payment_response.json()['response'] # 조회한 결제 정보


#         #### 결제정보 검증 후 저장
#         # DB에서 결제되어야하는 금액 조회

#         myclient = pymongo.MongoClient()
#         db_test = myclient["test"] # Local의 Test DB 접근
#         ordersdb = db_test.Order # Order Collection 생성 및 접근
#         user_oder_db = db_test.user_oder_db 

#         # Get amount to be paid from database
#         order = ordersdb.find_one({"merchant_uid": payment_data['merchant_uid']})
#         amount_to_be_paid = order['amount']

#         amount = payment_data['amount']
#         status = payment_data['status']

#         if amount == amount_to_be_paid: # 결제 금액 일치, 결제된 금액 = 결제되어야 하는 금액
#             # Save payment data to database
#             await ordersdb.update_one({"merchant_uid": merchant_uid}, {"$set": payment_data})

#         # token에서 유저정보 받기
#         try :
#             payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    
#         except:
#             raise HTTPException(status_code=401, detail='Invaild token')

#         print("payload : ", payload)

#         if 'email' in payload:
#             email = payload['email']
#         else:
#             email = payload['sub']


#         if status == "ready": # 가상계좌 발급
#                 # DB에 가상계좌 발급 정보 저장
#                 vbank_num = payment_data['vbank_num']
#                 vbank_date = payment_data['vbank_date']
#                 vbank_name = payment_data['vbank_name']

#                 await user_oder_db.update_one({"email": email}, {"$set": {vbank_num, vbank_date, vbank_name}})
               
#                 # 가상계좌 발급 안내 문자메시지 발송
#                 response.status_code = 200
#                 return {"status": "vbankIssued", "message": f"Virtual account issued successfully. Account info {vbank_num} {vbank_date} {vbank_name}"}
        
#         elif status == "paid": # 결제완료
#                 response.status_code = 200
#                 return {"status": "success", "message": "Payment successful"}
        
#         else: # 결제금액 불일치, 위/변조 된 결제
#             raise HTTPException(status_code=400, detail={"status": "forgery", "message": "위조된 결제시도"})
   
#     except Exception as e:
#         response.status_code = 400
#         return e
        






