import os
from dotenv import load_dotenv

# .env 파일 로드 (있는 경우)
load_dotenv()

# 환경 변수에서 DB 정보 가져오기 (없으면 기본값 사용)
# 보안을 위해 .env 파일에 실제 비밀번호를 설정하는 것을 권장합니다
DB_SERVER = os.getenv('DB_SERVER', 'ms0501.gabiadb.com')
DB_DATABASE = os.getenv('DB_DATABASE', 'yujin')
DB_USERNAME = os.getenv('DB_USERNAME', 'yujin')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'yj8630')  # 기본값 (보안 위험 - .env 사용 권장)

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
