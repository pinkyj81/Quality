import os
from dotenv import load_dotenv

# .env 파일 로드 (있는 경우)
load_dotenv()

# 환경 변수에서 DB 정보 가져오기
DB_SERVER = os.getenv('DB_SERVER')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# 로컬 개발 환경용 기본값 (환경 변수가 설정되지 않은 경우에만)
if not all([DB_SERVER, DB_DATABASE, DB_USERNAME, DB_PASSWORD]):
    print("경고: 일부 DB 환경 변수가 설정되지 않았습니다. 기본값을 사용합니다.")
    DB_SERVER = DB_SERVER or 'ms0501.gabiadb.com'
    DB_DATABASE = DB_DATABASE or 'yujin'
    DB_USERNAME = DB_USERNAME or 'yujin'
    DB_PASSWORD = DB_PASSWORD or 'yj8630'  # 로컬 개발용

def get_connection_string():
    """MSSQL 연결 문자열 반환"""
    return f"""
DRIVER={{ODBC Driver 17 for SQL Server}};
SERVER={DB_SERVER};
DATABASE={DB_DATABASE};
UID={DB_USERNAME};
PWD={DB_PASSWORD};
"""

def get_connection():
    """pyodbc 연결 객체 반환"""
    import pyodbc
    return pyodbc.connect(get_connection_string())
