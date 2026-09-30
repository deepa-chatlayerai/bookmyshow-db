-- ============================================================
-- BookMyShow Ticketing Backend — MySQL Schema
-- ============================================================

-- -------------------------------------------------------
-- 1. users
-- -------------------------------------------------------
CREATE TABLE users (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(120)        NOT NULL,
    email       VARCHAR(255)        NOT NULL,
    phone       VARCHAR(15)         NOT NULL,
    created_at  DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_email (email),
    UNIQUE KEY uq_users_phone (phone)
);

-- -------------------------------------------------------
-- 2. movies
-- -------------------------------------------------------
CREATE TABLE movies (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(255)    NOT NULL,
    duration_mins   SMALLINT UNSIGNED NOT NULL,
    language        VARCHAR(50)     NOT NULL,
    genre           VARCHAR(80)     NOT NULL,
    rating          CHAR(5),                        -- e.g. 'U/A', 'A'
    release_date    DATE            NOT NULL
);

-- -------------------------------------------------------
-- 3. theatres
-- -------------------------------------------------------
CREATE TABLE theatres (
    id      BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(255)    NOT NULL,
    city    VARCHAR(100)    NOT NULL,
    address TEXT            NOT NULL
);

-- -------------------------------------------------------
-- 4. screens
-- -------------------------------------------------------
CREATE TABLE screens (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    theatre_id  BIGINT UNSIGNED NOT NULL,
    name        VARCHAR(60)     NOT NULL,   -- e.g. 'Screen 1', 'Audi A'
    total_seats SMALLINT UNSIGNED NOT NULL,
    CONSTRAINT fk_screens_theatre FOREIGN KEY (theatre_id)
        REFERENCES theatres (id) ON DELETE CASCADE,
    UNIQUE KEY uq_screen_name_per_theatre (theatre_id, name)
);

-- -------------------------------------------------------
-- 5. seats
-- Each physical seat in a screen. Created once; never deleted.
-- -------------------------------------------------------
CREATE TABLE seats (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    screen_id   BIGINT UNSIGNED NOT NULL,
    row_label   CHAR(3)         NOT NULL,   -- e.g. 'A', 'B', 'AA'
    seat_number TINYINT UNSIGNED NOT NULL,  -- 1-based within the row
    seat_type   ENUM('REGULAR','PREMIUM','RECLINER') NOT NULL DEFAULT 'REGULAR',
    CONSTRAINT fk_seats_screen FOREIGN KEY (screen_id)
        REFERENCES screens (id) ON DELETE CASCADE,
    UNIQUE KEY uq_seat_position (screen_id, row_label, seat_number)
);

-- -------------------------------------------------------
-- 6. shows
-- A show = one screening of a movie on a specific screen at a specific time.
-- -------------------------------------------------------
CREATE TABLE shows (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    movie_id    BIGINT UNSIGNED NOT NULL,
    screen_id   BIGINT UNSIGNED NOT NULL,
    show_date   DATE            NOT NULL,
    start_time  TIME            NOT NULL,
    base_price  DECIMAL(8,2)    NOT NULL,
    CONSTRAINT fk_shows_movie  FOREIGN KEY (movie_id)  REFERENCES movies  (id),
    CONSTRAINT fk_shows_screen FOREIGN KEY (screen_id) REFERENCES screens (id),
    -- A screen can only run one show at a time
    UNIQUE KEY uq_show_slot (screen_id, show_date, start_time),
    INDEX idx_shows_date_screen (show_date, screen_id)  -- P2 query
);

-- -------------------------------------------------------
-- 7. show_seats
-- Per-show availability state for every seat.
-- This is the central table for concurrency control.
-- -------------------------------------------------------
CREATE TABLE show_seats (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    show_id         BIGINT UNSIGNED NOT NULL,
    seat_id         BIGINT UNSIGNED NOT NULL,
    status          ENUM('AVAILABLE','HELD','BOOKED') NOT NULL DEFAULT 'AVAILABLE',
    hold_expires_at DATETIME        NULL,           -- set when status = 'HELD'
    booking_id      BIGINT UNSIGNED NULL,           -- set when status = 'BOOKED'
    version         INT UNSIGNED    NOT NULL DEFAULT 0,  -- optimistic lock counter
    CONSTRAINT fk_ss_show FOREIGN KEY (show_id) REFERENCES shows (id),
    CONSTRAINT fk_ss_seat FOREIGN KEY (seat_id) REFERENCES seats (id),
    UNIQUE KEY uq_show_seat (show_id, seat_id),
    INDEX idx_ss_show_status (show_id, status),
    INDEX idx_ss_expires (hold_expires_at)  -- for the expiry sweep job
);

-- -------------------------------------------------------
-- 8. bookings
-- -------------------------------------------------------
CREATE TABLE bookings (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT UNSIGNED NOT NULL,
    show_id         BIGINT UNSIGNED NOT NULL,
    status          ENUM('PENDING','CONFIRMED','CANCELLED','FAILED') NOT NULL DEFAULT 'PENDING',
    total_amount    DECIMAL(10,2)   NOT NULL,
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_bookings_user FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_bookings_show FOREIGN KEY (show_id) REFERENCES shows (id),
    INDEX idx_bookings_user  (user_id),
    INDEX idx_bookings_show  (show_id)
);

-- Add the forward FK from show_seats → bookings (defined after bookings table)
ALTER TABLE show_seats
    ADD CONSTRAINT fk_ss_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (id) ON DELETE SET NULL;

-- -------------------------------------------------------
-- 9. payments
-- Idempotent: external_txn_id is UNIQUE to prevent double-credit.
-- -------------------------------------------------------
CREATE TABLE payments (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    booking_id      BIGINT UNSIGNED     NOT NULL,
    amount          DECIMAL(10,2)       NOT NULL,
    status          ENUM('PENDING','SUCCESS','FAILED','REFUNDED') NOT NULL DEFAULT 'PENDING',
    gateway         VARCHAR(60)         NOT NULL,   -- e.g. 'razorpay', 'stripe'
    external_txn_id VARCHAR(255)        NOT NULL,   -- gateway's transaction ID
    payload         JSON                NULL,       -- raw webhook body for audit
    created_at      DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_payments_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (id),
    UNIQUE KEY uq_external_txn (external_txn_id)    -- idempotency guarantee
);
