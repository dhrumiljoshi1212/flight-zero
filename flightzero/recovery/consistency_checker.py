from flightzero.application.reservation_service import ReservationService


def check_repository(repository) -> dict:
    """Read-only consistency check. This function never repairs data."""
    return ReservationService(repository).check()
