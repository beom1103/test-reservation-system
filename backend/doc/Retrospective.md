# 📝 프로젝트 회고 및 README (Retrospective)

이 문서는 본 프로젝트를 진행하면서 느꼈던 점, 아쉬웠던 점, 기술적 선택의 배경과 회고를 정리한 문서입니다.

---

## 🙋‍♂️ 개인적으로 느꼈던 아쉬운 점들

### 1. Python / FastAPI 환경 적응에 시간이 걸렸다

- 기존 TypeScript + nodejs 환경에 익숙했던 상태에서 Python 기반의 의존성 주입 (`Depends`), Pydantic + SQLModel 구조 DB 트랜잭션 처리 방식이 생소해 익숙해지기까지 시간이 필요했습니다.

> 그 결과, **서비스 구현과 테스트 작성 타이밍이 엇갈려서** 초반 테스트 커버리지를 충분히 확보하지 못했다는 점이 가장 아쉬웠습니다.

### 2. 테스트 코드가 대부분 "API 관점"으로만 구성됨

- `TestClient` 기반의 end-to-end 테스트 위주로 작성했기 때문에, **Service, Repository 계층에 대한 단위 테스트가 부족**했습니다

```python
# 서비스 로직 단위 테스트 예시가 부족했음 (아쉬움)
def test_confirm_reservation_logic():
    service = ReservationService(mocked_session)
    reservation = ...  # fixture or factory로 구성
    assert service.confirm(reservation).status == "confirmed"
```

- 실제 로직은 대부분 서비스 계층에 집중되어 있기 때문에, 이 계층을 단위 테스트로 쪼개는 것이 더 생산적이었을 것 같습니다.

---

## 🧠 정리

Python과 FastAPI에 대한 기초를 학습하면서, 구조 설계, 동시성 제약 처리, 역할 기반 권한 분리, 테스트 자동화 등 실무에서 필요한 백엔드 개발의 전반적인 요소들을 직접 설계하고 구현해볼 수 있었습니다.

물론, 처음 접하는 기술 스택이다 보니 서비스 계층 단위 테스트 부족, 테스트 속도와 구성 최적화 부족 등 일부 아쉬운 점도 있었지만, 전반적으로는 운영 환경을 고려한 구조적 설계와 의도는 충분히 반영되었다고 생각합니다.
