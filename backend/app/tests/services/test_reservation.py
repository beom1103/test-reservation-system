# import random
# import pytest
# import uuid
# from datetime import datetime, timedelta
# from sqlmodel import Session

# from app.models.reservations import Reservation, ReservationStatus, ReservationUpdate
# from app.models.tryouts import Tryout, TryoutUpdateRequest
# from app.models.users import User
# from app.services.reservations import ReservationService
# from app.core.exceptions import BadRequestError, AuthorizationError


# @pytest.fixture
# def user():
#     return User(id=uuid.uuid4(), is_superuser=False)


# @pytest.fixture
# def admin():
#     return User(id=uuid.uuid4(), is_superuser=True)


# def create_tryout(start_offset_days=2, confirmed_reserved_count=2):
#     now = datetime.now()
#     return Tryout(
#         id=random.randint(1, 2_000_000_000),
#         start_time=now + timedelta(days=start_offset_days),
#         registration_start_time=now - timedelta(days=1),
#         registration_end_time=now + timedelta(days=1),
#         max_capacity=10,
#         confirmed_reserved_count=confirmed_reserved_count,
#     )


# def create_reservation(user_id, tryout_id, seats=2, status=ReservationStatus.pending):
#     return Reservation(
#         id=random.randint(1, 2_000_000_000),
#         user_id=user_id,
#         tryout_id=tryout_id,
#         reserved_seats=seats,
#         status=status,
#     )


# def test_update_reservation_success(session: Session, user):
#     # 예약 수정이 성공하는 경우
#     tryout = create_tryout()
#     reservation = create_reservation(user.id, tryout.id)

#     session.add(tryout)
#     session.add(reservation)

#     service = ReservationService(session)
#     update_data = ReservationUpdate(reserved_seats=3)
#     result = service.update_reservation(user, reservation.id, update_data)

#     assert result.reserved_seats == 3


# # def test_update_with_no_change_raises_error(session: Session, user):
# #     # 변경사항이 없으면 에러 발생
# #     tryout = create_tryout()
# #     reservation = create_reservation(user.id, tryout.id, seats=2)

# #     session.add(tryout)
# #     session.add(reservation)
# #     session.commit()

# #     service = ReservationService(session)
# #     update_data = ReservationUpdate(reserved_seats=2)

# #     with pytest.raises(BadRequestError, match="변경된 데이터가 없습니다"):
# #         service.update_reservation(user, reservation.id, update_data)


# # def test_delete_reservation_after_exam_started(session: Session, user):
# #     # 시험 시작 이후에는 예약 삭제가 불가능해야 함
# #     tryout = create_tryout(start_offset_days=-1)
# #     reservation = create_reservation(user.id, tryout.id)

# #     session.add(tryout)
# #     session.add(reservation)
# #     session.commit()

# #     service = ReservationService(session)

# #     with pytest.raises(
# #         BadRequestError, match="시험 시작 이후에는 예약을 삭제할 수 없습니다"
# #     ):
# #         service.delete_reservation(reservation.id, current_user=user)


# # def test_admin_can_update_confirmed_reservation(session: Session, admin):
# #     # 어드민은 확정된 예약도 수정 가능
# #     tryout = create_tryout()
# #     reservation = create_reservation(
# #         admin.id, tryout.id, seats=2, status=ReservationStatus.confirmed
# #     )

# #     session.add(tryout)
# #     session.add(reservation)
# #     session.commit()

# #     service = ReservationService(session)
# #     update_data = ReservationUpdate(reserved_seats=3)
# #     result = service.update_reservation(admin, reservation.id, update_data)

# #     assert result.reserved_seats == 3


# # def test_user_cannot_update_confirmed_reservation(session: Session, user):
# #     # 일반 사용자는 확정된 예약을 수정할 수 없음
# #     tryout = create_tryout()
# #     reservation = create_reservation(
# #         user.id, tryout.id, seats=2, status=ReservationStatus.confirmed
# #     )

# #     session.add(tryout)
# #     session.add(reservation)
# #     session.commit()

# #     service = ReservationService(session)
# #     update_data = ReservationUpdate(reserved_seats=3)

# #     with pytest.raises(BadRequestError, match="확정된 예약은 수정할 수 없습니다"):
# #         service.update_reservation(user, reservation.id, update_data)
