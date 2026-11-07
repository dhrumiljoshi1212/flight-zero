# Architecture

```text
CLI -> ReservationService -> ReservationRepository protocol
                              |
                              v
                    JsonReservationRepository
                    - portalocker lock
                    - read/validate JSON
                    - enforce seat rule
                    - temp file + fsync + os.replace

ReservationService -> JsonlEventLog (separate append-only file)
```

Domain owns models, errors, and invariant detection. Application owns use cases. Infrastructure owns JSON, locks, and event storage. Recovery currently exposes read-only checking.

The lock surrounds each read-modify-write. All writers must use the same lock path. Atomic replacement and locking are local-prototype safeguards, not multi-host database transactions. Filesystem semantics vary.

The event append is not atomic with the reservation JSON replacement. A crash can create an event/state discrepancy. A later PostgreSQL design should consider a transactional outbox and a unique constraint preventing multiple active reservations for the same flight/seat.
