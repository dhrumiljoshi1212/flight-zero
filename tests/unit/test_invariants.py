from datetime import datetime, timezone
from flightzero.domain.invariants import find_violations
from flightzero.domain.models import Flight, Reservation, ReservationStatus


def test_duplicate_active_seat_is_detected():
    flights = {"F1": Flight("F1", ("A0",))}
    now = datetime.now(timezone.utc)
    rows = [
        Reservation("R1", "F1", "A0", ReservationStatus.CONFIRMED, now),
        Reservation("R2", "F1", "A0", ReservationStatus.CONFIRMED, now),
    ]
    assert any(x["code"] == "DUPLICATE_ACTIVE_SEAT" for x in find_violations(flights, rows))
