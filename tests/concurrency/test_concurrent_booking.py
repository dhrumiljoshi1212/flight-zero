from concurrent.futures import ThreadPoolExecutor
from flightzero.domain.errors import SeatAlreadyBooked
from flightzero.domain.models import ReservationStatus


def test_only_one_concurrent_booking_succeeds(repository):
    def attempt(_):
        try:
            return repository.book("FLIGHT-001", "A0")
        except SeatAlreadyBooked:
            return None

    with ThreadPoolExecutor(max_workers=20) as pool:
        outcomes = list(pool.map(attempt, range(20)))
    assert sum(item is not None for item in outcomes) == 1
    active = [r for r in repository.list_reservations()
              if r.status == ReservationStatus.CONFIRMED and r.flight_id == "FLIGHT-001" and r.seat_id == "A0"]
    assert len(active) == 1
