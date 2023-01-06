# import logging
# import datetime

# class MongoHandler(logging.Handler):
#     def __init__(self, level=logging.NOTSET, 
#                  host='localhost', port=27017, username=None, password=None, authMechanism='DEFAULT',
#                  databaseName='test', collectionName='log_db', capped=True, size=100000, isCollectionDrop=False,
#                  instanceName='default'):
#         import pymongo
#         import platform
        
#         logging.Handler.__init__(self, level) #// 부모 생성자 호출
        
#         # self.conn = pymongo.MongoClient(host=host, port=port, #// 몽고클라이언트를 만든다
#         #                                 username=username,
#         #                                 password=password,
#         #                                 authMechanism='DEFAULT')
#         self.conn = pymongo.MongoClient(host=host, port=port)
#         self.db = self.conn.get_database(databaseName) #// 데이터베이스를 가져온다
        
#         #// 데이터베이스 컬렉션을 가져온다
#         if collectionName in self.db.list_collection_names(): #// 존재한다면
#             if isCollectionDrop:
#                 self.db.drop_collection(collectionName) #// Drop하고
#                 self.collection = self.create_collection(collectionName) #// 다시 만든다
#             else:
#                 #// 가져온다
#                 self.collection = self.db.get_collection(collectionName)
#         else: #// 없다면
#             self.collection = self.create_collection(collectionName) #// 만든다
        
#         self.hostName     = platform.node() #// 호스트이름을 저장한다
#         self.instanceName = instanceName #// 인스턴스이름을 저장한다

#     def create_collection(self, collectionName):
#         #// 컬렉션이름으로 컬렉션을 만들고 리턴한다
#         return self.db.create_collection(collectionName, 
#                                          capped=True,    #// 고정크기 컬렉션
#                                          size=10000000)   #// 컬렉션 최대크기지정(단위: bytes)


#     def emit(self, record):
        
#         import socket
#         # import pygeoip

#         # Get the hostname of the current system
#         hostname = socket.gethostname()
        
        
#         # Get the IP address of the current system
#         ip_address = socket.gethostbyname(hostname)

#         # Initialize the GeoIP database, IP 주소 있는 DB 가져와서 도출해야할 듯
#         # geoip_db = pygeoip.GeoIP('/path/to/GeoLite2-Country.mmdb') 
#         # country = geoip_db.country_name_by_addr(ip_address)
#         # Log the IP address
#         logging.warning(f'IP Address: {ip_address}')
        
#         self.record = record

#         document = \
#         {
#             'when' : datetime.datetime.now(),       #// 현재일시
#             'created':record.created,               #// 현재일시
#             # 'asctime':record.asctime,               #// 사람이 읽을 수 있는, LogRecord 생성시간 
#             'localhostName': self.hostName,         #// 로컬 호스트명
#             'localInstanceName': self.instanceName, #// 로컬 인스턴스명
#             'ip_Address': ip_address,               #// ip 주소
#             # 'fileName': record.filename,            #// 파일명
#             'processName': record.processName,      #// 프로세스명
#             # 'threadName': record.threadName,        #// 쓰레드명
#             'functionName': record.funcName,        #// 함수명
#             'log_name': record.name,                #// 로깅 호출에 사용된 로거의 이름
#             'log_source_line': record.lineno,       #// 로깅 호출이 일어난 소스 행 번호
#             'log_source_file_path': record.pathname,#// 로깅 호출이 일어난 소스 파일의 전체 경로명
#             'log_function_name': record.funcName,   #// 로깅 호출을 포함하는 함수의 이름
#             'process_id': record.process,           #// 프로세스 ID
#             'process_Name': record.processName,     #// 프로세스 이름
#             'levelNumber': record.levelno,          #// 로그레벨(ex. 10)
#             'levelName': record.levelname,          #// 로그레벨명(ex. DEBUG)
#             'message': record.msg,                  #// 오류 메시지
#         }
#         self.collection.insert_one(document, bypass_document_validation=False)




    

    