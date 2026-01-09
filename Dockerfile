FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# FreeTDS 설치 (pymssql용, ODBC 드라이버보다 훨씬 간단)
RUN apt-get update && apt-get install -y \
    freetds-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 10000

# 앱 실행
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--workers", "2", "--timeout", "120"]
