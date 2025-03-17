# 1. 빌드 단계 (dependencies 설치)
FROM python:3.11-alpine as builder

WORKDIR /app

# Poetry 설치
RUN pip install poetry

# 환경 변수 설정 (Poetry 가상환경 비활성화)
ENV POETRY_VIRTUALENVS_CREATE=false

# pyproject.toml & poetry.lock 복사
COPY pyproject.toml poetry.lock /app/

# 의존성 설치 (운영 환경 패키지만 설치)
RUN poetry install --no-root 

# 2. 실행 단계
FROM python:3.11-alpine

WORKDIR /app

# 빌드 단계에서 설치한 패키지 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 프로젝트 코드 복사
COPY . /app

# 포트 설정 (FastAPI 기본 포트)
EXPOSE 8000

# FastAPI 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]