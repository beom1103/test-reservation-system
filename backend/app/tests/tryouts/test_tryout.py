from fastapi.testclient import TestClient

from app.core.config import settings


def test_get_tryout_list(
    client: TestClient, normal_user_token_headers0: dict[str, str]
) -> None:
    # Given: 로그인된 일반 사용자
    # When: 시험 일정 목록 조회 API 호출
    response = client.get(
        f"{settings.API_V1_STR}/tryouts",
        headers=normal_user_token_headers0,
    )

    # Then: 시험 목록이 반환되고, 각 일정에 isApplied 필드 포함
    assert response.status_code == 200
    content = response.json()
    assert "items" in content
    assert isinstance(content["items"], list)
    if content["items"]:
        assert "isApplied" in content["items"][0]


# ✅ 3일 이내 시작되는 시험에는 예약할 수 없음
def test_tryout_reservation_within_3_days_should_fail(
    client: TestClient, normal_user_token_headers0: dict[str, str]
) -> None:
    # Given: 시작까지 2일 남은 시험 (tryout_id=6~10 초기 데이터 기준)
    tryout_id = 6
    # When: 예약 신청 시도
    response = client.post(
        f"{settings.API_V1_STR}/tryouts/{tryout_id}/reserve?reserved_seats=1",
        headers=normal_user_token_headers0,
    )
    # Then: 예약 불가
    assert response.status_code == 400
    assert "신청 기간이 아닙니다." in response.text


# ✅ 동시간대 예약이 이미 존재할 경우 실패
def test_tryout_reservation_duplicate_timeslot_should_fail(
    client: TestClient, normal_user_token_headers0: dict[str, str]
) -> None:
    # Given: 같은 시간대에 예약 하나 생성
    first = client.post(
        f"{settings.API_V1_STR}/tryouts/1/reserve?reserved_seats=1",
        headers=normal_user_token_headers0,
    )
    assert first.status_code == 200

    # When: 같은 시간대의 다른 tryout 예약 시도 (tryout 1~5는 동일 시간대라고 가정)
    second = client.post(
        f"{settings.API_V1_STR}/tryouts/2/reserve?reserved_seats=1",
        headers=normal_user_token_headers0,
    )
    # Then: 실패
    assert second.status_code == 400
    assert "동시간대에 이미 예약된 시험이 존재합니다." in second.text


# ✅ 5만명 초과 예약 시도시 실패
def test_tryout_over_capacity_should_fail(
    client: TestClient,
    normal_user_token_headers0: dict[str, str],
    normal_user_token_headers1: dict[str, str],
) -> None:
    # Given: 1명 예약을 먼저 생성하고, 해당 tryout의 확정 인원을 max에 맞춰 둔 상태라 가정
    reserve = client.post(
        f"{settings.API_V1_STR}/tryouts/5/reserve?reserved_seats=1",
        headers=normal_user_token_headers0,
    )
    assert reserve.status_code == 200

    # When: max_capacity(50000)을 넘는 인원 신청
    response = client.post(
        f"{settings.API_V1_STR}/tryouts/5/reserve?reserved_seats=50000",
        headers=normal_user_token_headers1,
    )
    # Then: 실패
    assert response.status_code == 400
    assert "정원이 가득 찼습니다." in response.text


# ✅ 예약 신청 성공 시 응답 구조 확인
def test_tryout_reservation_success(
    client: TestClient, normal_user_token_headers0: dict[str, str]
) -> None:
    # Given: 예약 가능한 시험 ID (tryout_id=1)
    # When: 예약 신청
    response = client.post(
        f"{settings.API_V1_STR}/tryouts/1/reserve?reserved_seats=2",
        headers=normal_user_token_headers0,
    )
    # Then: 정상 예약 처리됨
    assert response.status_code == 200
    data = response.json()
    assert data["reserved_seats"] == 2
    assert data["status"] == "pending"
    assert data["tryout_id"] == 1


# ✅ 어드민은 시험을 신청할 수 없음
def test_tryout_reservation_admin_forbidden(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    # Given: 어드민 로그인 상태
    # When: 예약 신청 시도
    response = client.post(
        f"{settings.API_V1_STR}/tryouts/1/reserve?reserved_seats=1",
        headers=superuser_token_headers,
    )
    # Then: 금지됨
    assert response.status_code == 403
    assert "Admin은 시험 신청이 불가합니다." in response.text
