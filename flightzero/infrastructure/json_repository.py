import json
import os
import tempfile
from pathlib import Path
from uuid import uuid4

import portalocker

from flightzero.domain.errors import (
    DataFormatError, FlightNotFound, ReservationAlreadyCancelled,
    ReservationNotFound, SeatAlreadyBooked, SeatNotFound,
)
from flightzero.domain.models import Flight, Reservation, ReservationStatus, utc_now


class JsonReservationRepository:
    """Local JSON repository; every read-modify-write mutation uses one lock."""
    def __init__(self, data_path: Path, lock_path: Path | None = None):
        self.data_path = Path(data_path)
        self.lock_path = Path(lock_path) if lock_path else self.data_path.with_suffix(".lock")
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self):
        sample = {"flights": [{"flight_id": "FLIGHT-001", "seats": ["A0", "A1", "A2", "B0", "B1"]}],
                  "reservations": []}
        with portalocker.Lock(str(self.lock_path), mode="a", timeout=10):
            if not self.data_path.exists():
                self._atomic_write(sample)

    def _read(self):
        if not self.data_path.exists():
            raise DataFormatError(f"Data file missing: {self.data_path}; run `flightzero init`")
        try:
            data = json.loads(self.data_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("flights"), list) or not isinstance(data.get("reservations"), list):
                raise ValueError("expected object with flights and reservations arrays")
            return data
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise DataFormatError(f"Cannot read reservation data: {exc}") from exc

    def _write(self, data):
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{self.data_path.name}.", suffix=".tmp", dir=self.data_path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(data, stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, self.data_path)
            try:
                dir_fd = os.open(self.data_path.parent, os.O_RDONLY)
                try: os.fsync(dir_fd)
                finally: os.close(dir_fd)
            except OSError:
                pass
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    _atomic_write = _write

    @staticmethod
    def _decode(data):
        try:
            flights_list = [Flight(x["flight_id"], tuple(x["seats"])) for x in data["flights"]]
            flights = {f.flight_id: f for f in flights_list}
            if len(flights) != len(flights_list):
                raise ValueError("duplicate flight identifiers")
            reservations = [Reservation.from_dict(x) for x in data["reservations"]]
            return flights, reservations
        except (KeyError, TypeError, ValueError) as exc:
            raise DataFormatError(f"Invalid data structure: {exc}") from exc

    def list_flights(self):
        with portalocker.Lock(str(self.lock_path), mode="a", timeout=10):
            return self._decode(self._read())[0]

    def list_reservations(self):
        with portalocker.Lock(str(self.lock_path), mode="a", timeout=10):
            return self._decode(self._read())[1]

    def book(self, flight_id, seat_id):
        with portalocker.Lock(str(self.lock_path), mode="a", timeout=10):
            data = self._read()
            flights, reservations = self._decode(data)
            flight = flights.get(flight_id)
            if flight is None: raise FlightNotFound(f"Unknown flight: {flight_id}")
            if seat_id not in flight.seats: raise SeatNotFound(f"Unknown seat {seat_id} on {flight_id}")
            if any(r.flight_id == flight_id and r.seat_id == seat_id and r.status == ReservationStatus.CONFIRMED for r in reservations):
                raise SeatAlreadyBooked(f"Seat {seat_id} on {flight_id} is already booked")
            result = Reservation(str(uuid4()), flight_id, seat_id, ReservationStatus.CONFIRMED, utc_now())
            data["reservations"].append(result.to_dict())
            self._write(data)
            return result

    def cancel(self, reservation_id):
        with portalocker.Lock(str(self.lock_path), mode="a", timeout=10):
            data = self._read()
            _, reservations = self._decode(data)
            index = next((i for i, r in enumerate(reservations) if r.reservation_id == reservation_id), None)
            if index is None: raise ReservationNotFound(f"Unknown reservation: {reservation_id}")
            old = reservations[index]
            if old.status == ReservationStatus.CANCELLED:
                raise ReservationAlreadyCancelled(f"Reservation {reservation_id} is already cancelled")
            result = Reservation(old.reservation_id, old.flight_id, old.seat_id,
                                 ReservationStatus.CANCELLED, old.created_at, utc_now())
            data["reservations"][index] = result.to_dict()
            self._write(data)
            return result

    def availability(self, flight_id):
        with portalocker.Lock(str(self.lock_path), mode="a", timeout=10):
            flights, reservations = self._decode(self._read())
            if flight_id not in flights: raise FlightNotFound(f"Unknown flight: {flight_id}")
            occupied = {r.seat_id for r in reservations if r.flight_id == flight_id and r.status == ReservationStatus.CONFIRMED}
            return [seat for seat in flights[flight_id].seats if seat not in occupied]
