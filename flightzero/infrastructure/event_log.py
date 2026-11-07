import json
import os
from pathlib import Path
from uuid import uuid4
from flightzero.domain.models import Reservation, utc_now


class JsonlEventLog:
    """Append-only prototype log; not transactionally coupled to reservation JSON."""
    def __init__(self, path: Path):
        self.path = Path(path)

    def append_reservation_event(self, event_type: str, reservation: Reservation) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        event = {"event_id": str(uuid4()), "event_type": event_type,
                 "reservation_id": reservation.reservation_id, "flight_id": reservation.flight_id,
                 "seat_id": reservation.seat_id, "timestamp": utc_now().isoformat()}
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
