"""
로컬 테스트 및 디버깅용 스크립트
환경 설정과 DB 연결을 확인합니다.
"""
import os
import sys

print("=== 환경 설정 확인 ===")
print(f"Python 버전: {sys.version}")
print(f"작업 디렉토리: {os.getcwd()}")

# 환경 변수 확인
print("\n=== 환경 변수 확인 ===")
env_vars = ['DB_SERVER', 'DB_DATABASE', 'DB_USERNAME', 'DB_PASSWORD']
for var in env_vars:
    value = os.getenv(var)
    if value:
        # 비밀번호는 일부만 표시
        if var == 'DB_PASSWORD':
            print(f"{var}: {'*' * len(value)}")
        else:
            print(f"{var}: {value}")
    else:
        print(f"{var}: 설정 안 됨")

# db_config 테스트
print("\n=== DB 설정 테스트 ===")
try:
    from db_config import DB_SERVER, DB_DATABASE, DB_USERNAME, DB_PASSWORD, get_connection_string
    print(f"DB_SERVER: {DB_SERVER}")
    print(f"DB_DATABASE: {DB_DATABASE}")
    print(f"DB_USERNAME: {DB_USERNAME}")
    print(f"DB_PASSWORD: {'*' * len(DB_PASSWORD) if DB_PASSWORD else '없음'}")
    print("\n연결 문자열 생성 성공!")
except Exception as e:
    print(f"오류: {e}")

# pyodbc 테스트
print("\n=== pyodbc 드라이버 확인 ===")
try:
    import pyodbc
    drivers = pyodbc.drivers()
    print(f"사용 가능한 ODBC 드라이버: {drivers}")
    if not drivers:
        print("경고: ODBC 드라이버가 설치되지 않았습니다!")
except Exception as e:
    print(f"오류: {e}")

# 폰트 확인
print("\n=== 폰트 파일 확인 ===")
font_paths = [
    'fonts/malgun.ttf',
    'fonts/NanumGothic.ttf',
    'C:/Windows/Fonts/malgun.ttf'
]
for path in font_paths:
    exists = "✓" if os.path.exists(path) else "✗"
    print(f"{exists} {path}")

print("\n=== 테스트 완료 ===")
