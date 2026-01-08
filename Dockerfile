FROM python:3.11-slim

# 포트 설정 (Cloud Run은 기본적으로 PORT 환경변수를 제공, 기본값 8080)
ENV PORT=8080

WORKDIR /app

# 시스템 의존성 설치 (필요시)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run에서 요구하는 포트 리스닝 방식 적용
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
