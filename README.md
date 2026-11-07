# FLIGHTZERO
### The Airline Reservation Reliability & Chaos Engineering Laboratory

**Break the booking system. Watch it fight back.**

FLIGHTZERO is an experimental engineering platform built around a deceptively difficult problem: keeping airline seat reservations correct when many customers compete for the same seats, processes fail midway through operations, and stored data must be recovered safely.

Most booking demos show the happy path: select a seat, click Book, and display a confirmation. FLIGHTZERO focuses on what happens when the happy path disappears.

What if 500 customers try to reserve the same seat at once? What if a process crashes after reading reservation state but before completing a write? What if cancellation races with another operation? What evidence can prove that the system recovered correctly?

FLIGHTZERO is intended to become a laboratory where these scenarios can be reproduced, measured, inspected, and improved—with AI assisting the engineering investigation while deterministic software remains responsible for correctness.

> **Project status:** Early-stage starter implementation. The initial milestone is a local Python reservation core with JSON persistence, locking, atomic file replacement, a consistency checker, CLI commands, and automated tests. Advanced chaos experiments, distributed infrastructure, AI agents, and dashboards are roadmap items—not completed features.

---

## Table of contents

- [Why FLIGHTZERO exists](#why-flightzero-exists)
- [The problem being explored](#the-problem-being-explored)
- [Project objectives](#project-objectives)
- [Core capabilities](#core-capabilities)
- [What makes it different](#what-makes-it-different)
- [Current implementation](#current-implementation)
- [Architecture](#architecture)
- [Repository structure](#repository-structure)
- [Technology choices](#technology-choices)
- [Installation](#installation)
- [Quick start](#quick-start)
- [CLI reference](#cli-reference)
- [Running the tests](#running-the-tests)
- [Reservation correctness model](#reservation-correctness-model)
- [Concurrency and experiment philosophy](#concurrency-and-experiment-philosophy)
- [Persistence and recovery limitations](#persistence-and-recovery-limitations)
- [AI-assisted incident investigation](#ai-assisted-incident-investigation)
- [Security and safety](#security-and-safety)
- [Development workflow](#development-workflow)
- [Roadmap](#roadmap)
- [How to contribute](#how-to-contribute)
- [License](#license)

---

## Why FLIGHTZERO exists

An airline reservation system is a useful environment for studying reliability because a seat is a scarce resource. Two customers must never receive a confirmed reservation for the same seat on the same flight.

That simple rule becomes harder when operations overlap.

Consider this sequence:

1. Customer A requests seat `A0`.
2. Customer B requests seat `A0` at nearly the same time.
3. Both requests inspect the stored state.
4. Both see the seat as available.
5. Both attempt to save a reservation.

An unsafe implementation can accept both requests. This is a race condition: the result depends on the timing and interleaving of operations.

The same system must also define what happens when a cancellation overlaps with a booking, when storage is malformed, or when a process stops unexpectedly.

FLIGHTZERO makes these reliability questions the central product—not an afterthought.

## The problem being explored

The project investigates five related engineering challenges.

### 1. Concurrency correctness

How can the reservation engine guarantee that competing requests cannot create duplicate active seat assignments?

### 2. Failure handling

What happens if an operation fails between reading state and persisting its update? Can the system fail without leaving partially written state?

### 3. State consistency

How can the system independently inspect reservation records and identify impossible or contradictory states?

### 4. Recovery

After an interruption, what evidence is available to determine whether the stored state is valid? Which recovery actions are safe, and which require an operator to decide?

### 5. AI-assisted engineering

Can an AI assistant analyze structured incident evidence, identify likely causes, propose a regression test, and help an engineer investigate a failure without becoming an unsafe authority over reservation data?

---

## Project objectives

FLIGHTZERO is being developed around the following objectives:

- **Correctness:** enforce reservation invariants in deterministic application and storage code.
- **Reproducibility:** make failure scenarios repeatable using recorded parameters and seeds.
- **Observability:** record enough structured evidence to understand what happened.
- **Recoverability:** design explicit, verifiable recovery procedures.
- **Measurability:** report actual throughput, latency, conflicts, and invariant violations.
- **Explainability:** connect incident conclusions to logs, events, test cases, and source locations.
- **Safety:** isolate destructive experiments and require approval for consequential recovery actions.

The project is not intended to claim production readiness based on a successful demo. Reliability claims should be supported by tests and repeatable experiments.

## Core capabilities

The following describes the intended platform. The status column distinguishes the current starter from future work.

| Capability | Purpose | Status |
|---|---|---|
| Reservation domain model | Represent flights, seats, and reservations | Initial |
| Booking and cancellation | Execute core reservation operations | Initial |
| JSON persistence | Store local reservation state | Initial |
| File locking | Serialize local read-modify-write operations | Initial |
| Atomic state replacement | Avoid exposing a partially written JSON file | Initial |
| Consistency checker | Detect duplicate active seats and invalid references | Initial |
| CLI | Run operations from a terminal | Initial |
| Automated tests | Verify core behavior and contention | Initial |
| Chaos scenario runner | Run controlled fault experiments | Planned |
| Crash-point testing | Interrupt operations at known stages | Planned |
| Recovery journal | Track and verify recovery actions | Planned |
| Experiment recorder | Store repeatable experiment configurations and results | Planned |
| PostgreSQL adapter | Add transactional database persistence | Planned |
| Redis seat holds | Explore temporary reservation holds | Planned |
| AI incident investigator | Analyze evidence and propose diagnostics | Planned |
| Live observability dashboard | Visualize experiments and failures | Planned |

"Initial" means included in this starter codebase; it does not imply production-grade guarantees. Run the tests and inspect implementation details before relying on a capability.

## What makes it different

FLIGHTZERO is not intended to be another airline booking CRUD application.

Its central workflow is an engineering experiment:

1. Establish a known reservation state.
2. Define a failure or contention scenario.
3. Execute the scenario against isolated test data.
4. Capture operation outcomes and system evidence.
5. Check the reservation invariants.
6. Compare the result with the expected behavior.
7. Preserve the run so it can be reproduced.
8. Investigate failures and add regression tests.

### The long-term AI-versus-chaos concept

A future version may include two separate AI-assisted roles:

**Chaos Investigator / Scenario Designer**

- Proposes edge cases and race-condition scenarios.
- Suggests controlled failure points.
- Helps generate test cases from observed weaknesses.
- Does not attack real systems or run destructive actions without explicit authorization.

**Reliability Investigator**

- Reads a minimized incident bundle.
- Summarizes what the logs and events actually show.
- Produces root-cause hypotheses with supporting evidence.
- Suggests code areas and regression tests for human review.
- Does not silently change reservation state or apply patches.

These roles are an aspirational feature, not part of the initial working implementation. Deterministic tests—not an AI agent's statement—must decide whether a system invariant passed.

## Current implementation

The starter project provides a local vertical slice.

### Reservation operations

- Initialize sample flight data.
- Book a seat on a known flight.
- Reject an already-booked seat.
- Cancel an existing reservation.
- Make a cancelled seat available again.
- List available seats.

### Persistence

Reservation state is stored in a local JSON file. The repository uses a process-level lock around read-modify-write operations and writes updates to a temporary file before replacing the active state file.

### Consistency checking

A read-only checker examines the current data for conditions such as:

- Duplicate reservation identifiers.
- More than one active reservation for a flight/seat pair.
- Reservations referencing an unknown flight.
- Reservations referencing a seat not defined for that flight.

The checker reports findings. It does not repair data.

### Event history

Successful service operations can append structured JSONL events. This event log is a separate file from reservation state; the two writes are not one atomic transaction. See [Persistence and recovery limitations](#persistence-and-recovery-limitations).

---

## Architecture

The initial design separates business rules from command-line handling and storage.

```text
                     User / Developer
                            |
                            v
                      CLI commands
                            |
                            v
                  ReservationService
                    Application layer
                            |
                            v
              ReservationRepository protocol
                            |
                            v
               JsonReservationRepository
                  Infrastructure layer
                  /        |          \
                 v         v           v
             JSON file   File lock   Atomic replace
                 |
                 v
           Reservation state

                  ReservationService
                            |
                            v
                     JsonlEventLog
                    Append-only events

        Repository + reservation records
                            |
                            v
                 Consistency checker
                   Read-only report
```

### Domain layer

Location: `flightzero/domain/`

Contains:

- `models.py`: flight and reservation types, reservation statuses, timestamps, serialization helpers.
- `errors.py`: explicit exceptions for expected domain/application failures.
- `invariants.py`: read-only invariant detection.

The domain layer should remain independent of file paths, CLI arguments, database drivers, and AI APIs.

### Application layer

Location: `flightzero/application/`

Contains:

- `reservation_service.py`: booking, cancellation, availability, and consistency-check orchestration.
- `ports.py`: repository protocol that describes the storage operations the application needs.

The application layer should depend on the repository interface rather than directly on JSON implementation details.

### Infrastructure layer

Location: `flightzero/infrastructure/`

Contains:

- `json_repository.py`: local JSON-backed repository and locking boundary.
- `event_log.py`: append-only JSONL event writer.

A future PostgreSQL adapter should implement the same repository contract while providing database-level transaction and constraint guarantees.

### Recovery layer

Location: `flightzero/recovery/`

Currently provides a read-only consistency-check entry point. Repair workflows are deliberately not implemented in the starter.

### CLI layer

Location: `flightzero/cli/`

Parses command-line arguments, invokes application services, and prints results. Business rules should not be implemented in CLI handlers.

### Future experiment layers

`flightzero/chaos/` and `flightzero/experiments/` are reserved for controlled scenario execution and experiment recording. They are extension points, not a claim that a full chaos framework is already implemented.

## Repository structure

```text
FLIGHTZERO/
├── .github/
│   └── workflows/
│       └── tests.yml
├── data/
│   └── sample_reservations.json
├── docs/
│   ├── ARCHITECTURE.md
│   ├── INVARIANTS.md
│   └── ROADMAP.md
├── flightzero/
│   ├── __init__.py
│   ├── __main__.py
│   ├── domain/
│   │   ├── errors.py
│   │   ├── invariants.py
│   │   └── models.py
│   ├── application/
│   │   ├── ports.py
│   │   └── reservation_service.py
│   ├── infrastructure/
│   │   ├── event_log.py
│   │   └── json_repository.py
│   ├── recovery/
│   │   └── consistency_checker.py
│   ├── chaos/
│   ├── experiments/
│   └── cli/
│       └── commands.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── concurrency/
├── .env.example
├── .gitignore
├── CLAUDE_BUILD_GUIDE.md
├── README.md
├── START_HERE.md
└── pyproject.toml
```

Some directories are intentionally minimal placeholders for later milestones.

## Technology choices

| Technology | Role in the starter or roadmap |
|---|---|
| Python 3.12+ | Primary language |
| `portalocker` | Cross-platform process-level file locking |
| JSON | Local prototype reservation persistence |
| JSONL | Append-only prototype event records |
| `pytest` | Automated tests |
| `ruff` | Optional linting and formatting |
| PostgreSQL | Planned transactional persistence adapter |
| Redis | Optional future temporary seat-hold/cache layer |
| FastAPI | Possible future API layer |
| React | Possible future experiment dashboard |
| LLM API | Optional future incident-analysis assistant |

The initial project deliberately avoids introducing distributed infrastructure before the local reservation invariants are established.

---

## Installation

### 1. Check Python

```bash
python --version
```

Use Python 3.12 or newer.

### 2. Create a virtual environment

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\\Scripts\\Activate.ps1
```

### 3. Install the project

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

This installs the package in editable mode, the `portalocker` runtime dependency, and the development tools defined in `pyproject.toml`.

If installation fails, check your Python version and inspect the full error before changing dependency versions.

## Quick start

Run these commands from the project root.

### Initialize sample data

```bash
flightzero init
```

This creates `data/reservations.json` if it does not already exist. It does not overwrite an existing reservation file.

### Inspect consistency

```bash
flightzero check
```

Expected shape of a clean report:

```json
{
  "valid": true,
  "violations": [],
  "checked_reservations": 0
}
```

### Book a seat

```bash
flightzero book FLIGHT-001 A0
```

The command prints the reservation record, including its generated reservation ID. Save that ID if you want to cancel the reservation.

### Try a duplicate booking

Run the same command again:

```bash
flightzero book FLIGHT-001 A0
```

The second request should be rejected because the seat already has an active confirmed reservation.

### Check availability

```bash
flightzero availability FLIGHT-001
```

The booked seat should no longer appear in the available-seat list.

### Cancel a reservation

Replace the placeholder with the ID printed by the booking command:

```bash
flightzero cancel YOUR_RESERVATION_ID
```

The cancelled seat should become available again.

### Verify the final state

```bash
flightzero check
```

The checker should report no invariant violations for this normal sequence.

## CLI reference

The CLI supports a data-file option and an event-log option.

```bash
flightzero --help
flightzero init --help
```

| Command | Description |
|---|---|
| `flightzero init` | Create sample data if the data file does not exist |
| `flightzero book FLIGHT_ID SEAT_ID` | Attempt to reserve a seat |
| `flightzero cancel RESERVATION_ID` | Cancel a confirmed reservation |
| `flightzero availability FLIGHT_ID` | List seats not currently confirmed |
| `flightzero check` | Return a read-only consistency report |

### Use a separate data file

Global options must appear before the subcommand:

```bash
flightzero --data /tmp/flightzero-demo.json init
flightzero --data /tmp/flightzero-demo.json book FLIGHT-001 A0
flightzero --data /tmp/flightzero-demo.json check
```

### Use a separate event log

```bash
flightzero --events /tmp/flightzero-demo-events.jsonl book FLIGHT-001 A0
```

For experiments, always use a dedicated temporary data file and event log.

## Running the tests

Install development dependencies first:

```bash
pip install -e ".[dev]"
```

Run all tests:

```bash
pytest
```

Run only unit tests:

```bash
pytest -q tests/unit
```

Run integration tests:

```bash
pytest -q tests/integration
```

Run concurrency tests:

```bash
pytest -q tests/concurrency
```

Run with coverage:

```bash
pytest --cov=flightzero --cov-report=term-missing
```

The concurrency test uses multiple workers competing for the same seat and checks that only one active reservation is created. This is a useful first correctness test, not proof of multi-host or production scalability.

## Reservation correctness model

The project uses explicit invariants to define acceptable system state.

| Invariant | Meaning |
|---|---|
| Unique active seat assignment | A flight/seat pair has no more than one active confirmed reservation |
| Cancellation releases seat | A cancelled reservation no longer occupies its seat |
| Unknown flight rejection | Booking an unknown flight fails without mutation |
| Unknown seat rejection | Booking an undefined seat fails without mutation |
| No partial failed booking | A failed request does not create a partial reservation |
| Explicit cancellation semantics | Unknown and already-cancelled reservations have defined outcomes |
| Referential integrity | Reservations refer to known flights and seats |
| Durable state before success | The repository does not return success before state replacement completes |

The canonical list is maintained in [`docs/INVARIANTS.md`](docs/INVARIANTS.md).

## Concurrency and experiment philosophy

A meaningful reliability experiment should define:

- Initial system state.
- Scenario and expected behavior.
- Number of workers or requests.
- Timing/delay parameters.
- Random seed, if randomness is used.
- Expected business conflicts.
- Unexpected system failures.
- Final invariant-check result.
- Exact software/environment version.

A duplicate booking rejection is an expected business outcome, not necessarily an application failure.

A future experiment report should distinguish:

- **Accepted:** operation completed successfully.
- **Conflict:** operation was correctly rejected by a business rule.
- **Failed:** unexpected system or infrastructure error.
- **Invariant violation:** final state broke a correctness rule.

Never publish benchmark values unless they were measured and the environment and methodology are recorded.

## Persistence and recovery limitations

The starter uses a JSON file and a process-level lock. The lock surrounds each repository read-modify-write operation. The update is written to a temporary file in the same directory, flushed, and replaced with `os.replace`.

This is a local prototype. It is not equivalent to a transactional database.

Important limitations:

1. File-lock behavior depends on the operating system and filesystem.
2. All writers must use the same lock path and repository protocol.
3. Network filesystems and multi-host deployments require separate validation.
4. The reservation JSON update and event JSONL append are separate operations.
5. A crash between those operations can leave an event/state discrepancy.
6. The consistency checker detects selected data problems but does not repair them.
7. The starter does not implement a full crash-recovery journal.

A future database implementation should consider transactions, database constraints, an outbox for event delivery, and explicit recovery semantics.

## AI-assisted incident investigation

AI is a planned assistant for engineering diagnosis—not a source of truth for reservation state.

A future incident investigator may receive a redacted incident bundle and produce:

- A timeline of observed events.
- A summary of errors and invariant-check findings.
- Root-cause hypotheses clearly separated from facts.
- Evidence references supporting each hypothesis.
- Suggested diagnostic steps.
- A proposed regression test.

AI-generated conclusions must be reviewed by an engineer. AI must not silently edit reservation records, apply unreviewed patches, or execute arbitrary commands.

## Security and safety

- Use synthetic reservation data for development and testing.
- Never commit API keys, passwords, tokens, or private environment files.
- Do not log passenger personal information.
- Treat log content and AI output as untrusted input.
- Keep destructive chaos scenarios disabled by default.
- Run experiments in temporary directories or disposable environments.
- Require explicit operator approval before recovery actions that change state.
- Preserve evidence and backups before any future repair operation.

## Development workflow

Recommended contribution workflow:

1. Create a focused branch.
2. Read the relevant architecture and invariant documentation.
3. Add or update a test for the intended behavior.
4. Implement the smallest safe change.
5. Run targeted tests.
6. Run the full test suite.
7. Update documentation.
8. Report actual test output and known limitations.

Do not weaken an invariant just to make a test pass. If an invariant needs to change, document the business and technical reasoning.

## Roadmap

### Stage 1 — Reliable local core

- Typed domain models.
- Safe booking and cancellation.
- JSON persistence with a documented locking boundary.
- Atomic state-file replacement.
- Read-only consistency checker.
- Unit, integration, and concurrency tests.

### Stage 2 — Concurrency laboratory

- Configurable worker counts.
- Contention and cancellation-race scenarios.
- Deterministic scenario parameters.
- Experiment IDs and JSON result artifacts.
- Measured throughput and latency reports.

### Stage 3 — Fault injection and recovery

- Deterministic crash points.
- Child-worker interruption in isolated environments.
- Restart and recovery tests.
- Recovery journal and reconciliation.
- Operator approval and post-recovery invariant verification.

### Stage 4 — Distributed infrastructure

- PostgreSQL repository adapter.
- Database uniqueness constraints.
- Transaction-isolation tests.
- Optional Redis-based temporary seat holds.
- Multi-process and multi-instance experiments.

### Stage 5 — AI incident investigator

- Redacted incident bundles.
- Evidence-linked root-cause hypotheses.
- Diagnostic recommendations.
- Suggested regression tests.
- Human approval for all consequential changes.

### Stage 6 — Observability interface

- Experiment dashboard.
- Live or replayed metrics.
- Failure timelines.
- Contention visualization.
- Measured before-and-after comparisons.

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the concise milestone plan.

## How to contribute

Contributions are welcome, especially in:

- Race-condition and failure-mode test design.
- Repository adapter design.
- Persistence correctness.
- Reproducible chaos scenarios.
- Experiment metrics and reporting.
- Documentation and architecture review.

Before submitting a pull request, include:

- The problem being solved.
- The invariant or behavior affected.
- Tests added or updated.
- Commands run and their actual results.
- Any remaining limitations.

## License

This project is distributed under the MIT License. See [`LICENSE`](LICENSE) when present in the repository.

---

**FLIGHTZERO is an engineering experiment in making reservation systems explainable, testable, and resilient. The goal is not to claim that failures never happen; the goal is to make failures reproducible, visible, and recoverable.**
