import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# .env 파일 로드 (있는 경우)
load_dotenv()

# 환경 변수에서 DB 정보 가져오기
DB_SERVER = os.getenv('DB_SERVER')
DB_PORT = os.getenv('DB_PORT', '1433')  # 기본 포트
DB_DATABASE = os.getenv('DB_DATABASE')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# 디버깅: 환경 변수 확인 (비밀번호는 마스킹)
logger.info(f"DB_SERVER: {DB_SERVER}")
logger.info(f"DB_PORT: {DB_PORT}")
logger.info(f"DB_DATABASE: {DB_DATABASE}")
logger.info(f"DB_USERNAME: {DB_USERNAME}")
logger.info(f"DB_PASSWORD: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'None'}")

# 로컬 개발 환경용 기본값 (환경 변수가 설정되지 않은 경우에만)
if not all([DB_SERVER, DB_DATABASE, DB_USERNAME, DB_PASSWORD]):
    logger.warning("일부 DB 환경 변수가 설정되지 않았습니다. 기본값을 사용합니다.")
    DB_SERVER = DB_SERVER or 'ms0501.gabiadb.com'
    DB_DATABASE = DB_DATABASE or 'yujin'
    DB_USERNAME = DB_USERNAME or 'yujin'
    DB_PASSWORD = DB_PASSWORD or 'yj8630'  # 로컬 개발용

def get_connection_string():
    """pymssql 연결 딕셔너리 반환"""
    return {
        'server': DB_SERVER,
        'port': int(DB_PORT),
        'database': DB_DATABASE,
        'user': DB_USERNAME,
        'password': DB_PASSWORD,
        'charset': 'utf8',
        'timeout': 30,
        'login_timeout': 30
    }

def get_connection():
    """pymssql 연결 객체 반환"""
    import pymssql
    return pymssql.connect(**get_connection_string())
