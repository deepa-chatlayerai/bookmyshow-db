# BookMyShow — Ticketing Backend DB Design

A MySQL schema for a BookMyShow-scale ticketing platform covering seat-level locking, timed holds, and idempotent payment webhooks.

---

## Files

| File              | Purpose                                                            |
| ----------------- | ------------------------------------------------------------------ |
| `schema.sql`      | `CREATE TABLE` statements — all entities, indexes, and constraints |
| `sample_data.sql` | `INSERT` statements with realistic sample rows                     |
| `p2_query.sql`    | P2 solution — lists all shows on a given date at a given theatre   |
| `DESIGN.md`       | Entity list, normalization proof, and concurrency strategy         |

---

## Quick Start

```bash
mysql -u root -p < schema.sql
mysql -u root -p < sample_data.sql
mysql -u root -p < p2_query.sql   # edit the WHERE clause params first
```

---

## Entity Overview

| Table        | Purpose                                                      |
| ------------ | ------------------------------------------------------------ |
| `users`      | Platform users who make bookings                             |
| `movies`     | Movie catalogue                                              |
| `theatres`   | Physical cinema locations                                    |
| `screens`    | Auditoriums inside a theatre                                 |
| `seats`      | Fixed physical seats in a screen                             |
| `shows`      | One screening of a movie on a screen at a date/time          |
| `show_seats` | Per-show availability state for each seat (concurrency core) |
| `bookings`   | A user's purchase attempt for one or more seats              |
| `payments`   | Payment records with idempotency via `external_txn_id`       |
# BookMyShow DB — P1 & P2 Solution
