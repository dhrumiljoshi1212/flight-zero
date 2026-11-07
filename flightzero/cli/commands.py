import argparse
import json
from pathlib import Path

from flightzero.application.reservation_service import ReservationService
from flightzero.domain.errors import FlightZeroError
from flightzero.infrastructure.event_log import JsonlEventLog
from flightzero.infrastructure.json_repository import JsonReservationRepository


def main():
    parser = argparse.ArgumentParser(prog="flightzero")
    parser.add_argument("--data", type=Path, default=Path("data/reservations.json"))
    parser.add_argument("--events", type=Path, default=Path("data/events.jsonl"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    book = sub.add_parser("book")
    book.add_argument("flight_id")
    book.add_argument("seat_id")
    cancel = sub.add_parser("cancel")
    cancel.add_argument("reservation_id")
    avail = sub.add_parser("availability")
    avail.add_argument("flight_id")
    sub.add_parser("check")
    args = parser.parse_args()
    repo = JsonReservationRepository(args.data)
    if args.command == "init":
        repo.initialize()
        print(f"Initialized {args.data}")
        return 0
    service = ReservationService(repo, JsonlEventLog(args.events))
    try:
        if args.command == "book":
            result = service.book_seat(args.flight_id, args.seat_id)
            print(json.dumps(result.to_dict(), indent=2))
        elif args.command == "cancel":
            result = service.cancel_reservation(args.reservation_id)
            print(json.dumps(result.to_dict(), indent=2))
        elif args.command == "availability":
            print(json.dumps({"flight_id": args.flight_id, "available_seats": service.availability(args.flight_id)}, indent=2))
        elif args.command == "check":
            report = service.check()
            print(json.dumps(report, indent=2))
            return 0 if report["valid"] else 2
    except FlightZeroError as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
