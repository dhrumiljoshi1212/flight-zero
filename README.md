# FLIGHTZERO

**Break the booking system. Watch it fight back.**

FLIGHTZERO is an airline reservation reliability and chaos-engineering laboratory. This starter includes a local JSON reservation engine, process-level file locking, atomic state-file replacement, booking/cancellation use cases, a read-only consistency checker, a CLI, and tests.

## Quick start

Requires Python 3.12+.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e ".[dev]"
flightzero init
flightzero check
flightzero book FLIGHT-001 A0
flightzero availability FLIGHT-001
pytest
```

Cancel using the reservation ID printed by `book`:

```bash
flightzero cancel RESERVATION_ID
```

Use `--data PATH` and `--events PATH` to select alternate files.

## Current scope and limitations

This is a local prototype, not a production airline platform. It has no payments, authentication, distributed multi-node guarantees, or AI agent yet. JSON state replacement and event-log append are separate operations, so a crash between them can cause an event/state discrepancy. File-lock and durability semantics depend on the OS and filesystem.

Never use real passenger data in experiments. Correctness is enforced by deterministic code and tests, not by AI.

See `CLAUDE_BUILD_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/INVARIANTS.md`, and `docs/ROADMAP.md`.
