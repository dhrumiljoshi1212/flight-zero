from collections import Counter
from flightzero.domain.models import Flight, Reservation, ReservationStatus


def find_violations(flights: dict[str, Flight], reservations: list[Reservation]) -> list[dict]:
    issues = []
    for rid, count in Counter(r.reservation_id for r in reservations).items():
        if count > 1:
            issues.append({"code": "DUPLICATE_RESERVATION_ID", "reservation_id": rid, "count": count})
    active = {}
    for r in reservations:
        flight = flights.get(r.flight_id)
        if flight is None:
            issues.append({"code": "UNKNOWN_FLIGHT", "reservation_id": r.reservation_id})
            continue
        if r.seat_id not in flight.seats:
            issues.append({"code": "UNKNOWN_SEAT", "reservation_id": r.reservation_id})
        if r.status == ReservationStatus.CONFIRMED:
            active.setdefault((r.flight_id, r.seat_id), []).append(r.reservation_id)
    for (flight_id, seat_id), ids in active.items():
        if len(ids) > 1:
            issues.append({"code": "DUPLICATE_ACTIVE_SEAT", "flight_id": flight_id,
                           "seat_id": seat_id, "reservation_ids": ids})
    return issues
