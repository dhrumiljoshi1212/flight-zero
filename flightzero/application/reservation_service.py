from flightzero.domain.invariants import find_violations


class ReservationService:
    def __init__(self, repository, event_log=None):
        self.repository = repository
        self.event_log = event_log

    def book_seat(self, flight_id, seat_id):
        reservation = self.repository.book(flight_id, seat_id)
        if self.event_log:
            self.event_log.append_reservation_event("RESERVATION_CREATED", reservation)
        return reservation

    def cancel_reservation(self, reservation_id):
        reservation = self.repository.cancel(reservation_id)
        if self.event_log:
            self.event_log.append_reservation_event("RESERVATION_CANCELLED", reservation)
        return reservation

    def availability(self, flight_id):
        return self.repository.availability(flight_id)

    def check(self):
        flights = self.repository.list_flights()
        reservations = self.repository.list_reservations()
        violations = find_violations(flights, reservations)
        return {"valid": not violations, "violations": violations,
                "checked_reservations": len(reservations)}
