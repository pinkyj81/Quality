# QualityInspec - 공정능력 분석 시스템

Flask 기반 품질 관리 대시보드로 MSSQL 데이터베이스에서 공정 데이터를 분석하고 Cp/Cpk 값을 계산합니다.

## 기능

- 제품 코드별 실측 데이터 조회
- Spec별 평균, 표준편차, Cp, Cpk 계산
- 히스토그램 시각화
- PDF 리포트 생성

## 로컬 실행

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 패키지 설치
pip install -r requirements.txt
```

### 2. 데이터베이스 설정

`.env` 파일을 생성하고 DB 정보 입력:

```env
DB_SERVER=your_server.com
DB_DATABASE=your_database
DB_USERNAME=your_username
DB_PASSWORD=your_password
```

### 3. 한글 폰트 설정 (선택사항)

PDF 생성을 위해 `fonts/` 폴더에 한글 폰트 파일 복사:
- Windows: `malgun.ttf` 또는 `NanumGothic.ttf`
- Linux: NanumGothic 설치 필요

### 4. 실행

```bash
python app.py
```

브라우저에서 `http://localhost:5001` 접속

## 웹 호스팅 배포

### Render 배포 (추천)

1. **GitHub에 코드 푸시**

2. **Render에서 배포**:
   - [Render](https://render.com) 로그인
   - **New** > **Web Service** 선택
   - GitHub 리포지토리 연결
   
3. **설정**:
   - **Build Command**: `bash build.sh`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3

4. **환경 변수 설정** (Environment 탭):
   ```
   DB_SERVER=ms0501.gabiadb.com
   DB_DATABASE=yujin
   DB_USERNAME=yujin
   DB_PASSWORD=your_password
   ```

5. **중요**: Render는 기본적으로 root 권한이 없어서 `build.sh`가 실패할 수 있습니다.
   대신 **Dockerfile**을 사용하세요 (아래 참조).

### Render 배포 (Dockerfile 사용 - 권장)

Render에서는 Dockerfile이 더 안정적입니다. 다음 내용으로 `Dockerfile` 생성:

```dockerfile
FROM python:3.11-slim

# ODBC 드라이버 설치
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg2 \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev \
    && apt-get clean

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
```

Render 설정:
- Build Command: (비워두기)
- Start Command: (비워두기)
- Docker를 자동 감지합니다

### Railway 배포

1. [Railway](https://railway.app)에서 New Project
2. Deploy from GitHub repo 선택
3. 환경 변수 추가 (위와 동일)
4. 자동 배포됨

### PythonAnywhere 배포

1. [PythonAnywhere](https://www.pythonanywhere.com) 가입
2. Files 탭에서 코드 업로드
3. Web 탭에서 Flask app 설정
4. `.env` 파일에 DB 정보 입력

## 주의사항

### 보안
- `.env` 파일은 절대 Git에 커밋하지 마세요
- `.gitignore`에 `.env`가 포함되어 있습니다

### 데이터베이스 접근
- DB 서버의 방화벽에서 호스팅 서버 IP 허용 필요
- ODBC Driver 17 for SQL Server 필요

### 한글 폰트
- Windows에서만 테스트됨
- Linux 배포 시 `fonts/` 폴더에 폰트 파일 필요

## 파일 구조

```
QualityInspec/
├── app.py              # Flask 앱 메인 파일
├── db_config.py        # DB 연결 설정
├── requirements.txt    # Python 패키지
├── Procfile           # 웹 서버 실행 설정
├── runtime.txt        # Python 버전
├── .env.example       # 환경 변수 예시
├── .gitignore         # Git 제외 파일
├── fonts/             # 한글 폰트 (선택)
├── static/            # 정적 파일
│   └── hist/          # 히스토그램 이미지
└── templates/         # HTML 템플릿
    ├── index.html
    └── report.html
```

## 문제 해결

### ODBC 드라이버 오류
Linux에서는 다음 명령어로 설치:
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### 한글 폰트 깨짐
`fonts/` 폴더에 `.ttf` 파일 추가

### DB 연결 오류
- DB 서버 방화벽 설정 확인
- `.env` 파일의 정보 확인

## 라이선스

MIT
