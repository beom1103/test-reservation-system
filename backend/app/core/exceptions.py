class TryoutNotFoundError(Exception):
    pass


class AlreadyReservedError(Exception):
    pass


class TryoutFullError(Exception):
    pass


class InvalidReservationPeriodError(Exception):
    pass


class ReservationNotFoundError(Exception):
    pass


class AuthorizationError(Exception):
    pass
