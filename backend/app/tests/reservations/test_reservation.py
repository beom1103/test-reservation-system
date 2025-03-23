from fastapi.testclient import TestClient

from app.core.config import settings


# ✅ 본인 예약 목록 조회
def test_get_own_reservations(
    client: TestClient, normal_user_token_headers0: dict[str, str]
) -> None:
    reserve = client.post(
        f"{settings.API_V1_STR}/tryouts/2/reserve?reserved_seats=1",
        headers=normal_user_token_headers0,
    )
    assert reserve.status_code == 200

    response = client.get(
        f"{settings.API_V1_STR}/reservations",
        headers=normal_user_token_headers0,
    )
    assert response.status_code == 200
    content = response.json()
    assert "items" in content
    assert all(r["tryout_id"] for r in content["items"])


# ✅ 예약 단건 조회 성공
def test_get_reservation_by_id(
    client: TestClient, normal_user_token_headers0: dict[str, str]
) -> None:
    reserve = client.post(
        f"{settings.API_V1_STR}/tryouts/3/reserve?reserved_seats=1",
        headers=normal_user_token_headers0,
    )
    reservation_id = reserve.json()["id"]

    response = client.get(
        f"{settings.API_V1_STR}/reservations/{reservation_id}",
        headers=normal_user_token_headers0,
    )
    assert response.status_code == 200
    assert response.json()["id"] == reservation_id


# ✅ 예약 수정 성공
def test_update_reservation(
    client: TestClient, normal_user_token_headers0: dict[str, str]
) -> None:
    reserve = client.post(
        f"{settings.API_V1_STR}/tryouts/4/reserve?reserved_seats=2",
        headers=normal_user_token_headers0,
    )
    reservation_id = reserve.json()["id"]

    response = client.patch(
        f"{settings.API_V1_STR}/reservations/{reservation_id}",
        headers=normal_user_token_headers0,
        json={"reserved_seats": 4},
    )
    assert response.status_code == 200
    assert response.json()["reserved_seats"] == 4


# ✅ 예약 삭제 후 상태 확인
def test_delete_reservation(
    client: TestClient, normal_user_token_headers0: dict[str, str]
) -> None:
    reserve = client.post(
        f"{settings.API_V1_STR}/tryouts/5/reserve?reserved_seats=1",
        headers=normal_user_token_headers0,
    )
    reservation_id = reserve.json()["id"]

    response = client.delete(
        f"{settings.API_V1_STR}/reservations/{reservation_id}/delete",
        headers=normal_user_token_headers0,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


# ✅ 예약 확정 처리
def test_admin_confirm_reservation(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers0: dict[str, str],
) -> None:
    reserve = client.post(
        f"{settings.API_V1_STR}/tryouts/1/reserve?reserved_seats=2",
        headers=normal_user_token_headers0,
    )
    reservation_id = reserve.json()["id"]

    response = client.post(
        f"{settings.API_V1_STR}/reservations/{reservation_id}/confirm",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"


# ✅ 본인 아닌 예약 조회/수정 시도 차단
def test_reservation_access_denied(
    client: TestClient,
    normal_user_token_headers0: dict[str, str],
    normal_user_token_headers1: dict[str, str],
) -> None:
    reserve = client.post(
        f"{settings.API_V1_STR}/tryouts/2/reserve?reserved_seats=1",
        headers=normal_user_token_headers0,
    )
    reservation_id = reserve.json()["id"]

    response = client.get(
        f"{settings.API_V1_STR}/reservations/{reservation_id}",
        headers=normal_user_token_headers1,
    )
    assert response.status_code in (400, 403)


# ✅ 확정 예약은 수정 불가
def test_confirmed_reservation_cannot_be_updated(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers0: dict[str, str],
) -> None:
    reserve = client.post(
        f"{settings.API_V1_STR}/tryouts/1/reserve?reserved_seats=1",
        headers=normal_user_token_headers0,
    )
    reservation_id = reserve.json()["id"]

    confirm = client.post(
        f"{settings.API_V1_STR}/reservations/{reservation_id}/confirm",
        headers=superuser_token_headers,
    )
    assert confirm.status_code == 200

    update = client.patch(
        f"{settings.API_V1_STR}/reservations/{reservation_id}",
        headers=normal_user_token_headers0,
        json={"reserved_seats": 5},
    )
    assert update.status_code == 400
    assert "확정된 예약은 수정할 수 없습니다" in update.text


# ✅ 확정 예약은 수정 불가
def test_confirmed_reservation_admin_can_be_updated(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers0: dict[str, str],
) -> None:
    reserve = client.post(
        f"{settings.API_V1_STR}/tryouts/1/reserve?reserved_seats=1",
        headers=normal_user_token_headers0,
    )
    reservation_id = reserve.json()["id"]

    confirm = client.post(
        f"{settings.API_V1_STR}/reservations/{reservation_id}/confirm",
        headers=superuser_token_headers,
    )
    assert confirm.status_code == 200

    update = client.patch(
        f"{settings.API_V1_STR}/reservations/{reservation_id}",
        headers=superuser_token_headers,
        json={"reserved_seats": 5},
    )
    assert update.status_code == 200


# ✅ [Admin] 확정된 예약도 삭제 가능
def test_admin_can_delete_confirmed_reservation(
    client: TestClient,
    superuser_token_headers: dict[str, str],
    normal_user_token_headers0: dict[str, str],
) -> None:
    reserve = client.post(
        f"{settings.API_V1_STR}/tryouts/2/reserve?reserved_seats=1",
        headers=normal_user_token_headers0,
    )
    reservation_id = reserve.json()["id"]

    confirm = client.post(
        f"{settings.API_V1_STR}/reservations/{reservation_id}/confirm",
        headers=superuser_token_headers,
    )
    assert confirm.status_code == 200

    delete = client.delete(
        f"{settings.API_V1_STR}/reservations/{reservation_id}/delete",
        headers=superuser_token_headers,
    )
    assert delete.status_code == 200
    assert delete.json()["status"] == "deleted"
