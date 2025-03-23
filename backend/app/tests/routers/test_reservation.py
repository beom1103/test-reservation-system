from fastapi.testclient import TestClient

from app.core.config import settings


def test_create_reservation(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.post(
        f"{settings.API_V1_STR}/tryouts/1/reserve?reserved_seats=3",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["tryout_id"] == 1
    assert data["reserved_seats"] == 3


def test_get_reservation_list(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    response = client.get(
        f"{settings.API_V1_STR}/reservations",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "items" in content
    assert isinstance(content["items"], list)


def test_update_reservation(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    create_res = client.post(
        f"{settings.API_V1_STR}/tryouts/2/reserve?reserved_seats=2",
        headers=normal_user_token_headers,
    )

    reservation_id = create_res.json()["id"]

    update_data = {"reserved_seats": 4}
    response = client.patch(
        f"{settings.API_V1_STR}/reservations/{reservation_id}",
        headers=normal_user_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["reserved_seats"] == 4


def test_delete_reservation(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    create_res = client.post(
        f"{settings.API_V1_STR}/tryouts/3/reserve?reserved_seats=1",
        headers=normal_user_token_headers,
    )
    reservation_id = create_res.json()["id"]

    response = client.delete(
        f"{settings.API_V1_STR}/reservations/{reservation_id}/delete",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_admin_confirm_reservation(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    user_res = client.post(
        f"{settings.API_V1_STR}/tryouts/4/reserve?reserved_seats=2",
        headers=superuser_token_headers,
    )
    reservation_id = user_res.json()["id"]

    response = client.post(
        f"{settings.API_V1_STR}/reservations/{reservation_id}/confirm",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
