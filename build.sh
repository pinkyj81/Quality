#!/bin/bash

# Render.com 빌드 스크립트 (Linux용 ODBC 드라이버 설치)

echo "==> Installing system dependencies..."

# Microsoft ODBC Driver 17 for SQL Server 설치
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Build complete!"
