# Reservation invariants

1. At most one active `CONFIRMED` reservation per flight/seat.
2. A cancelled reservation does not occupy its seat.
3. Unknown flights/seats fail without mutation.
4. Failed bookings do not leave partial records.
5. Unknown cancellation fails without mutation.
6. Repeated cancellation has explicit behavior.
7. Successful mutations produce audit events (subject to the documented cross-file crash limitation).
8. The checker detects duplicate active seats.
9. The checker detects duplicate IDs and unknown flight/seat references.
10. Success is returned only after the state file replacement completes.

Tests should cover each invariant, including concurrent contention.
