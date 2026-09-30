# Design Document — BookMyShow DB

## 1. Entities and Attributes

### users

| Column     | Type            | Constraints             |
| ---------- | --------------- | ----------------------- |
| id         | BIGINT UNSIGNED | PK, AUTO_INCREMENT      |
| name       | VARCHAR(120)    | NOT NULL                |
| email      | VARCHAR(255)    | NOT NULL, UNIQUE        |
| phone      | VARCHAR(15)     | NOT NULL, UNIQUE        |
| created_at | DATETIME        | NOT NULL, DEFAULT NOW() |

### movies

| Column        | Type              | Constraints        |
| ------------- | ----------------- | ------------------ |
| id            | BIGINT UNSIGNED   | PK, AUTO_INCREMENT |
| title         | VARCHAR(255)      | NOT NULL           |
| duration_mins | SMALLINT UNSIGNED | NOT NULL           |
| language      | VARCHAR(50)       | NOT NULL           |
| genre         | VARCHAR(80)       | NOT NULL           |
| rating        | CHAR(5)           | nullable           |
| release_date  | DATE              | NOT NULL           |

### theatres

| Column  | Type            | Constraints        |
| ------- | --------------- | ------------------ |
| id      | BIGINT UNSIGNED | PK, AUTO_INCREMENT |
| name    | VARCHAR(255)    | NOT NULL           |
| city    | VARCHAR(100)    | NOT NULL           |
| address | TEXT            | NOT NULL           |

### screens

| Column      | Type              | Constraints               |
| ----------- | ----------------- | ------------------------- |
| id          | BIGINT UNSIGNED   | PK, AUTO_INCREMENT        |
| theatre_id  | BIGINT UNSIGNED   | FK → theatres.id          |
| name        | VARCHAR(60)       | NOT NULL                  |
| total_seats | SMALLINT UNSIGNED | NOT NULL                  |
| —           | —                 | UNIQUE (theatre_id, name) |

### seats

| Column      | Type             | Constraints                                |
| ----------- | ---------------- | ------------------------------------------ |
| id          | BIGINT UNSIGNED  | PK, AUTO_INCREMENT                         |
| screen_id   | BIGINT UNSIGNED  | FK → screens.id                            |
| row_label   | CHAR(3)          | NOT NULL                                   |
| seat_number | TINYINT UNSIGNED | NOT NULL                                   |
| seat_type   | ENUM             | REGULAR / PREMIUM / RECLINER               |
| —           | —                | UNIQUE (screen_id, row_label, seat_number) |

### shows

| Column     | Type            | Constraints                               |
| ---------- | --------------- | ----------------------------------------- |
| id         | BIGINT UNSIGNED | PK, AUTO_INCREMENT                        |
| movie_id   | BIGINT UNSIGNED | FK → movies.id                            |
| screen_id  | BIGINT UNSIGNED | FK → screens.id                           |
| show_date  | DATE            | NOT NULL                                  |
| start_time | TIME            | NOT NULL                                  |
| base_price | DECIMAL(8,2)    | NOT NULL                                  |
| —          | —               | UNIQUE (screen_id, show_date, start_time) |

### show_seats

| Column          | Type            | Constraints                |
| --------------- | --------------- | -------------------------- |
| id              | BIGINT UNSIGNED | PK, AUTO_INCREMENT         |
| show_id         | BIGINT UNSIGNED | FK → shows.id              |
| seat_id         | BIGINT UNSIGNED | FK → seats.id              |
| status          | ENUM            | AVAILABLE / HELD / BOOKED  |
| hold_expires_at | DATETIME        | nullable — set when HELD   |
| booking_id      | BIGINT UNSIGNED | FK → bookings.id, nullable |
| version         | INT UNSIGNED    | optimistic lock counter    |
| —               | —               | UNIQUE (show_id, seat_id)  |

### bookings

| Column       | Type            | Constraints                              |
| ------------ | --------------- | ---------------------------------------- |
| id           | BIGINT UNSIGNED | PK, AUTO_INCREMENT                       |
| user_id      | BIGINT UNSIGNED | FK → users.id                            |
| show_id      | BIGINT UNSIGNED | FK → shows.id                            |
| status       | ENUM            | PENDING / CONFIRMED / CANCELLED / FAILED |
| total_amount | DECIMAL(10,2)   | NOT NULL                                 |
| created_at   | DATETIME        | NOT NULL                                 |
| updated_at   | DATETIME        | NOT NULL, ON UPDATE                      |

### payments

| Column          | Type            | Constraints                           |
| --------------- | --------------- | ------------------------------------- |
| id              | BIGINT UNSIGNED | PK, AUTO_INCREMENT                    |
| booking_id      | BIGINT UNSIGNED | FK → bookings.id                      |
| amount          | DECIMAL(10,2)   | NOT NULL                              |
| status          | ENUM            | PENDING / SUCCESS / FAILED / REFUNDED |
| gateway         | VARCHAR(60)     | NOT NULL                              |
| external_txn_id | VARCHAR(255)    | NOT NULL, **UNIQUE**                  |
| payload         | JSON            | nullable — raw webhook body           |
| created_at      | DATETIME        | NOT NULL                              |
| updated_at      | DATETIME        | NOT NULL, ON UPDATE                   |

---

## 2. Sample Rows

### users

| id  | name         | email             | phone      |
| --- | ------------ | ----------------- | ---------- |
| 1   | Arjun Mehta  | arjun@example.com | 9876543210 |
| 2   | Priya Sharma | priya@example.com | 9123456780 |

### movies

| id  | title         | duration_mins | language | genre           |
| --- | ------------- | ------------- | -------- | --------------- |
| 1   | Kalki 2898 AD | 180           | Telugu   | Sci-Fi / Action |
| 2   | Stree 2       | 135           | Hindi    | Horror Comedy   |

### theatres

| id  | name                       | city   |
| --- | -------------------------- | ------ |
| 1   | PVR Cinemas – Phoenix Mall | Mumbai |
| 2   | INOX – Lulu Mall           | Kochi  |

### shows (theatre 1, date 2024-10-01)

| id  | movie         | screen   | show_date  | start_time | base_price |
| --- | ------------- | -------- | ---------- | ---------- | ---------- |
| 1   | Kalki 2898 AD | Screen 1 | 2024-10-01 | 10:00      | ₹250       |
| 2   | Kalki 2898 AD | Screen 1 | 2024-10-01 | 14:00      | ₹300       |
| 3   | Stree 2       | Screen 2 | 2024-10-01 | 11:30      | ₹200       |

### show_seats (show 1)

| show_id | seat_id | status    | hold_expires_at | booking_id |
| ------- | ------- | --------- | --------------- | ---------- |
| 1       | 1       | BOOKED    | NULL            | 1          |
| 1       | 2       | BOOKED    | NULL            | 1          |
| 1       | 3       | AVAILABLE | NULL            | NULL       |

### payments

| id  | booking_id | amount | status  | gateway  | external_txn_id    |
| --- | ---------- | ------ | ------- | -------- | ------------------ |
| 1   | 1          | 500.00 | SUCCESS | razorpay | rzp_live_abc123XYZ |

---

## 3. Normalization

### 1NF — First Normal Form

All columns hold atomic, single-valued data. There are no repeating groups or arrays. For example, a booking's seats are stored as individual rows in `show_seats`, not as a comma-separated list.

### 2NF — Second Normal Form

Every non-key column depends on the **entire** primary key.  
All tables use a single-column surrogate PK (`id`), so there can be no partial dependency. For example, in `show_seats`, `status` and `hold_expires_at` depend on the full `(show_id, seat_id)` combination (enforced as a UNIQUE key), not on just one part of it.

### 3NF — Third Normal Form

No transitive dependencies exist. For example:

- `screens.theatre_id` tells us which theatre a screen belongs to; the theatre's `city` and `address` live only in `theatres`, not duplicated in `screens`.
- `shows` stores `base_price` for the show; per-seat pricing differences would be handled via `seats.seat_type`, not by denormalizing price into `show_seats`.

### BCNF — Boyce–Codd Normal Form

Every determinant is a candidate key.

- In `show_seats`, the `UNIQUE (show_id, seat_id)` constraint makes this pair a candidate key. All other columns (`status`, `hold_expires_at`, `booking_id`, `version`) are determined by this composite key and by nothing else.
- In `shows`, the `UNIQUE (screen_id, show_date, start_time)` constraint is the natural candidate key (a screen can only show one thing at a time). All non-key attributes depend on this and on the surrogate `id`, both of which are candidate keys.

---

## 4. Concurrency & Locking Strategy

### The problem

Thousands of users may try to book the same seat simultaneously. Without protection, two transactions can both read a seat as `AVAILABLE` and both commit a `BOOKED` record — a double-booking.

### Approach: Pessimistic locking per seat row

**Seat selection (hold phase)**

```sql
START TRANSACTION;

-- Lock the target rows so no other transaction can change them
-- until this transaction commits or rolls back.
SELECT id, status
FROM   show_seats
WHERE  show_id = 1
  AND  seat_id IN (3, 4)
  AND  status  = 'AVAILABLE'
FOR UPDATE;                    -- acquires row-level X-locks

-- Only proceed if we got all requested seats back.
-- If any seat was already locked by another transaction,
-- this statement blocks until that transaction ends, then
-- re-evaluates — if the status changed to HELD/BOOKED, 0 rows
-- are returned and we abort.

UPDATE show_seats
SET    status          = 'HELD',
       hold_expires_at = DATE_ADD(NOW(), INTERVAL 10 MINUTE),
       booking_id      = :new_booking_id
WHERE  show_id = 1
  AND  seat_id IN (3, 4)
  AND  status  = 'AVAILABLE';

-- If rows_affected < seats_requested → rollback (someone else got there first)
COMMIT;
```

**Why this prevents double-booking:**  
`FOR UPDATE` acquires exclusive row locks. The second concurrent transaction trying to lock the same rows will **block** until the first commits. After the first commits, the second re-reads `status = 'HELD'` and finds 0 matching rows, so it aborts cleanly.

### Hold expiry

A background job (cron or Redis TTL-triggered Lambda) runs every minute:

```sql
UPDATE show_seats
SET    status          = 'AVAILABLE',
       hold_expires_at = NULL,
       booking_id      = NULL
WHERE  status          = 'HELD'
  AND  hold_expires_at < NOW();
```

The `INDEX idx_ss_expires (hold_expires_at)` makes this sweep fast even at scale.

Redis can also be used to store `hold:{show_id}:{seat_id}` keys with a 10-minute TTL. On expiry, a Redis keyspace notification fires the release logic — this offloads the sweep entirely from the DB.

### Idempotent payment webhooks

The `payments.external_txn_id` column has a `UNIQUE` constraint. When a webhook arrives:

```sql
INSERT INTO payments (booking_id, amount, status, gateway, external_txn_id, payload)
VALUES (:booking_id, :amount, 'SUCCESS', 'razorpay', :txn_id, :raw_json)
ON DUPLICATE KEY UPDATE
    status    = VALUES(status),
    payload   = VALUES(payload),
    updated_at = NOW();
```

If the same webhook fires twice (network retry), the second `INSERT` hits the duplicate key and becomes a no-op update. The booking confirmation logic is therefore safe to run inside this upsert without risk of double-confirming.

### Index strategy

| Index                   | Table      | Purpose                                           |
| ----------------------- | ---------- | ------------------------------------------------- |
| `idx_shows_date_screen` | shows      | P2 query — filter by date + screen (theatre join) |
| `idx_ss_show_status`    | show_seats | Count available seats per show efficiently        |
| `idx_ss_expires`        | show_seats | Hold-expiry sweep                                 |
| `idx_bookings_user`     | bookings   | Fetch a user's booking history                    |
| `uq_show_seat`          | show_seats | Enforce one status row per (show, seat)           |
| `uq_external_txn`       | payments   | Idempotency for payment webhooks                  |
