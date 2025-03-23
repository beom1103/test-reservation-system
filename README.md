# 🧪 Tryout Reservation API

온라인 시험 플랫폼을 위한 예약 API 서버입니다.
고객은 시험 일정을 조회하고 예약을 신청하며, 어드민은 예약을 확정 및 관리할 수 있습니다.

---

## 🏗️ 기술 스택

- **FastAPI** – Python 웹 프레임워크
- **SQLModel** – SQLAlchemy + Pydantic 기반 ORM
- **PostgreSQL** – 관계형 데이터베이스
- **Docker Compose** – 로컬 환경 및 의존성 구성
- **Pytest / Coverage** – 테스트 및 커버리지 측정
- **Ruff, Mypy** – 린팅 및 타입 검사

---

## 📁 주요 폴더 구조

```bash
backend/
├── app/
│   ├── alembic/             # 마이그레이션 스크립트
│   ├── core/                # 설정, 보안, 트랜잭션 유틸리티
│   ├── models/              # Pydantic / SQLModel 모델
│   ├── repository/          # DB 쿼리 추상화
│   ├── routers/             # API 라우터
│   ├── services/            # 비즈니스 로직
│   ├── tests/               # 테스트 코드
│   ├── main.py              # FastAPI 엔트리포인트
│   ├── dependencies.py      # Depends 관련 공통 처리
│   └── backend_pre_start.py # 초기화 스크립트
├── htmlcov/                 # 커버리지 리포트
├── pyproject.toml           # 의존성 관리
├── Dockerfile
└── scripts/
```

---

## 🚀 실행 방법

### Docker 실행

```bash
docker-compose up --build
```

- 백엔드: [http://localhost:8000](http://localhost:8000)
- Swagger 문서: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔐 인증 및 권한

- 로그인: `/api/v1/utils/login/access-token`
- 권한은 `is_superuser` 여부로 구분
- 일반 사용자: 시험 조회 및 예약 신청
- 어드민: 모든 예약 관리 및 확정 가능

---

## 📌 기능 요약

| 기능           | 고객 (User)    | 어드민 (Admin) |
| -------------- | -------------- | -------------- |
| 시험 일정 조회 | ✅             | ✅             |
| 시험 예약 신청 | ✅             | ❌             |
| 예약 조회      | 본인 예약만    | 전체 예약      |
| 예약 수정/삭제 | 확정 전 본인만 | 전체 가능      |
| 예약 확정      | ❌             | ✅             |

---

## 🧪 테스트

```bash
cd backend
bash ./scripts/test.sh
```

> 커버리지 리포트는 `/backend/htmlcov/index.html`에서 확인할 수 있습니다.

### 🧪 테스트용 초기 데이터 (자동 생성)

`app/db.py`의 `init_db()`를 통해 초기 데이터가 자동으로 생성됩니다:

- ✅ **어드민 계정**:

  - 이메일: `admin@example.com`
  - 비밀번호: `.env`의 `FIRST_SUPERUSER_PASSWORD` 값 사용

- ✅ **일반 유저 10명**:

  - 이메일: `user0@example.com` ~ `user9@example.com`
  - 비밀번호: `password123`

- ✅ **시험 일정 10개**:
  - 앞의 5개는 예약 가능 (시험일 10일 후)
  - 뒤의 5개는 예약 불가 (시험일 2일 후)

---

## 📚 API 문서

### 🛣️ 주요 API 라우트

#### [인증]

- `POST /api/v1/utils/login/access-token` : 액세스 토큰 발급 (OAuth2)

#### [시험 일정 Tryouts]

- `GET /api/v1/tryouts` : 시험 일정 목록 조회
- `GET /api/v1/tryouts/{id}` : 시험 일정 상세 조회
- `POST /api/v1/tryouts/{id}/reserve` : 시험 일정 예약 신청

#### [예약 Reservations]

- `GET /api/v1/reservations` : 예약 목록 조회 (본인 or 어드민 전체)
- `GET /api/v1/reservations/{id}` : 예약 단건 조회
- `PATCH /api/v1/reservations/{id}` : 예약 수정
- `DELETE /api/v1/reservations/{id}/delete` : 예약 삭제
- `POST /api/v1/reservations/{id}/confirm` : 예약 확정 (어드민 전용)

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc (정적 스타일): [http://localhost:8000/redoc](http://localhost:8000/redoc)

> Swagger 문서는 FastAPI에서 자동 생성되며, 실제 요청/응답 예시도 포함되어 있습니다.
