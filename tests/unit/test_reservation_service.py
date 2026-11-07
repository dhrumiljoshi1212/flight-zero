import pytest
from flightzero.application.reservation_service import ReservationService
from flightzero.domain.errors import (
    FlightNotFound, ReservationAlreadyCancelled, ReservationNotFound,
    SeatAlreadyBooked, SeatNotFound,
)
from flightzero.domain.models import ReservationStatus


def test_booking_and_duplicate_rejection(repository):
    service = ReservationService(repository)
    first = service.book_seat("FLIGHT-001", "A0")
    assert first.status == ReservationStatus.CONFIRMED
    with pytest.raises(SeatAlreadyBooked):
        service.book_seat("FLIGHT-001", "A0")


def test_unknown_flight_and_seat(repository):
    with pytest.raises(FlightNotFound):
        repository.book("MISSING", "A0")
    with pytest.raises(SeatNotFound):
        repository.book("FLIGHT-001", "NOPE")


def test_cancel_releases_seat_and_repeat_is_rejected(repository):
    service = ReservationService(repository)
    reservation = service.book_seat("FLIGHT-001", "A0")
    service.cancel_reservation(reservation.reservation_id)
    assert "A0" in service.availability("FLIGHT-001")
    with pytest.raises(ReservationAlreadyCancelled):
        service.cancel_reservation(reservation.reservation_id)


def test_unknown_cancel(repository):
    with pytest.raises(ReservationNotFound):
        repository.cancel("missing")
