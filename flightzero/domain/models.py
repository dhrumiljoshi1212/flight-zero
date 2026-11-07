from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ReservationStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Flight:
    flight_id: str
    seats: tuple[str, ...]

    def __post_init__(self):
        if not self.flight_id.strip() or not self.seats:
            raise ValueError("flight ID and at least one seat are required")
        if len(set(self.seats)) != len(self.seats):
            raise ValueError("seat identifiers must be unique")


@dataclass(frozen=True)
class Reservation:
    reservation_id: str
    flight_id: str
    seat_id: str
    status: ReservationStatus
    created_at: datetime
    cancelled_at: datetime | None = None

    def to_dict(self) -> dict:
        result = asdict(self)
        result["status"] = self.status.value
        result["created_at"] = self.created_at.isoformat()
        result["cancelled_at"] = self.cancelled_at.isoformat() if self.cancelled_at else None
        return result

    @classmethod
    def from_dict(cls, raw: dict):
        try:
            created = datetime.fromisoformat(raw["created_at"])
            cancelled = datetime.fromisoformat(raw["cancelled_at"]) if raw.get("cancelled_at") else None
            if created.tzinfo is None or (cancelled is not None and cancelled.tzinfo is None):
                raise ValueError("timestamps must be timezone-aware")
            return cls(str(raw["reservation_id"]), str(raw["flight_id"]), str(raw["seat_id"]),
                       ReservationStatus(raw["status"]), created, cancelled)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid reservation record: {exc}") from exc
