# FLIGHTZERO — Elaborated Build Guide for Claude Code

## Mission

Evolve the existing airline reservation project into **FLIGHTZERO**, a reliability and chaos-engineering laboratory.

**Tagline: Break the booking system. Watch it fight back.**

The long-term platform will let developers run controlled experiments against a reservation engine, observe contention and failures, verify invariants, investigate incidents with AI, and evaluate recovery strategies.

This starter is intentionally small. First make the core correct, reproducible, and testable. Do not build a flashy dashboard or autonomous AI patcher before the reservation engine is trustworthy.

## First: inspect the existing repository

If this scaffold is being merged into the older `airline_seat_reservation_system` repository:

1. Print the repository tree.
2. Read its README, project configuration, CLI, models, services, persistence, locking, backup workflow, and tests.
3. Identify existing command behavior and data formats.
4. Run existing tests and record actual results.
5. Propose a migration plan identifying what to reuse, adapt, or replace.
6. Do not overwrite working code blindly or assume paths in an old README still exist.

Preserve compatibility with existing commands where practical. Explain any breaking changes before making them.

## Product vision

FLIGHTZERO will eventually have six capabilities:

1. **Reservation core:** correct booking and cancellation under contention.
2. **Chaos engine:** controlled fault injection in disposable environments.
3. **Consistency checker:** read-only verification of reservation invariants.
4. **Recovery engine:** explicit, auditable recovery of supported incomplete operations.
5. **Experiment recorder:** reproducible scenario configuration and measured outcomes.
6. **AI incident investigator:** evidence-grounded analysis and suggested regression tests.

A dashboard comes after the metrics and experiment model are stable.

## Critical safety principle

AI must not be in the correctness path. Deterministic application code, storage constraints, transactions/locking, and tests enforce correctness. AI may summarize evidence, form root-cause hypotheses, recommend code changes, and draft tests. It must not silently modify reservation data, apply unreviewed patches, or execute arbitrary commands.

Use synthetic data. Keep destructive scenarios opt-in, bounded, isolated, and recoverable.

## First milestone: reliable local vertical slice

Complete these steps before adding ambitious features:

1. Load a known flight and seats.
2. Book an available seat.
3. Reject a second active booking for the same flight/seat.
4. Cancel a confirmed reservation.
5. Make the cancelled seat available again.
6. Run a read-only consistency check.
7. Run a multi-worker contention test against temporary data.
8. Record actual test results and limitations.

Do not add PostgreSQL, Redis, Celery, a frontend, Kubernetes, or an external LLM API in this milestone unless a compelling existing compatibility need exists.

## Architecture boundaries

- **Domain:** entities, value rules, domain errors, invariants. No CLI, JSON, lock, web, or AI-provider imports.
- **Application:** booking/cancellation use cases and repository interfaces.
- **Infrastructure:** JSON persistence, locking, event storage, and future adapters.
- **Chaos:** controlled scenarios that call application interfaces using disposable data.
- **Recovery:** read-only detection first; repair is separate and requires operator approval.
- **Experiments:** run IDs, seeds, scenario configuration, timestamps, outcomes, metrics.
- **AI agents (future):** consume minimized, redacted incident bundles and return evidence-linked hypotheses.

## Non-negotiable invariants

Document and test these requirements:

1. At most one active confirmed reservation per flight/seat pair.
2. A cancelled reservation does not occupy its seat.
3. Unknown flights and seats are rejected without mutation.
4. Failed bookings do not leave partial reservations.
5. Unknown reservation cancellation is rejected without mutation.
6. Repeated cancellation has defined, tested behavior.
7. Successful state changes produce audit events.
8. The checker detects duplicate active reservations.
9. The checker detects duplicate reservation IDs and unknown flight/seat references.
10. A mutation is not reported successful before the state-file replacement completes.
11. Concurrency tests prove correctness, not merely successful process exit.

Do not claim linearizability, crash safety, or production readiness unless implementation and tests justify those claims.

## Persistence requirements

The starter uses JSON and a process-level lock. Treat this as a local prototype.

- Hold the same lock around the complete read-modify-write operation.
- Ensure every writer uses the same lock path.
- Write a temporary file in the same directory.
- Flush and `fsync` where supported, then replace the destination atomically.
- Clean up temporary files on failure.
- Never silently reset malformed data.
- Keep backups separate from active state.
- Document OS/filesystem assumptions.
- Do not store passenger personal data or secrets in fixtures.

The reservation JSON replacement and JSONL event append are separate filesystem operations. A crash between them can cause a missing or unmatched event. Do not describe them as one atomic transaction. A later database-backed design should use a transactionally coupled outbox or another explicit consistency mechanism.

## Concurrency experiments

Run only against temporary synthetic data:

- Many workers book the same seat.
- Artificial delays widen the read/write race window.
- Invalid request storms verify non-mutation.
- Multiple workers cancel the same reservation.

Record parameters, worker count, seed, and outcomes. Separate expected business conflicts from unexpected infrastructure errors. Never stress-test the user's real reservation data.

## Future chaos engineering

After the core is reliable, add bounded fault injection:

- Terminate a child worker at deterministic crash points.
- Pause operations at test hooks.
- Simulate transient repository errors.
- Simulate process restarts and recovery.
- Add network failures only after introducing a networked service.

Do not randomly kill arbitrary processes or corrupt a developer's filesystem. Every scenario needs timeouts, cleanup, explicit opt-in, and disposable data.

## Recovery design

Begin with a read-only consistency report. It should list violations, affected identifiers, and evidence.

Later recovery actions must explain the proposed change, require operator approval, preserve a pre-recovery snapshot, record an audit event, be idempotent where possible, and verify invariants afterward. Never guess which reservation should win a conflict without a defined business rule.

## AI incident investigator

Only after core correctness and experiment records are stable, add an optional LLM adapter.

Input should be a minimized incident bundle: scenario metadata, relevant events, structured exceptions, consistency findings, and relevant code/test references.

Output should distinguish observed facts from hypotheses, attach evidence to each hypothesis, suggest diagnostic steps, and propose regression tests. Require human review for all code/data changes. Do not send credentials, passenger data, or unrestricted repository contents to an external model.

## Benchmark integrity

Measure rather than invent:

- Total requests and worker count.
- Successful bookings.
- Expected conflicts.
- Unexpected errors.
- Throughput and latency percentiles.
- Invariant violations.
- Recovery duration, when implemented.

Record environment details when comparing runs. A large request count alone is not proof of production scalability.

## How Claude should work

For each change:

1. Explain intended behavior.
2. Add/update tests.
3. Implement the smallest reasonable change.
4. Run targeted tests.
5. Run the full test suite.
6. Update documentation.
7. Report exact commands and actual results.
8. List remaining risks and limitations.

Do not fabricate test output, benchmark results, or completed features.

## First task for Claude

1. Summarize the existing architecture and conflicts.
2. Verify package installation.
3. Run tests.
4. Fix issues in the starter.
5. Add tests for malformed data, unknown identifiers, repeated cancellation, and contention.
6. Verify CLI commands.
7. Update README with exact tested commands and results.

Do not start AI-agent work until the reliable core and tests are sound.

## Definition of success

FLIGHTZERO should become a credible engineering laboratory, not a flashy demo. Every claim is backed by reproducible experiments. Every recovery is auditable. Every AI recommendation is reviewable. Correctness comes before autonomy.
