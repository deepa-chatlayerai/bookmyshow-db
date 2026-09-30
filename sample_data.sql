-- ============================================================
-- BookMyShow — Sample Data
-- ============================================================

-- users
INSERT INTO users (name, email, phone) VALUES
  ('Arjun Mehta',   'arjun@example.com',  '9876543210'),
  ('Priya Sharma',  'priya@example.com',  '9123456780'),
  ('Rohan Kapoor',  'rohan@example.com',  '9988776655');

-- movies
INSERT INTO movies (title, duration_mins, language, genre, rating, release_date) VALUES
  ('Kalki 2898 AD',    180, 'Telugu', 'Sci-Fi / Action', 'U/A', '2024-06-27'),
  ('Stree 2',         135, 'Hindi',  'Horror Comedy',   'U/A', '2024-08-15'),
  ('Devara: Part 1',  166, 'Telugu', 'Action Drama',    'U/A', '2024-09-27');

-- theatres
INSERT INTO theatres (name, city, address) VALUES
  ('PVR Cinemas – Phoenix Mall', 'Mumbai',    'LBS Marg, Kurla West, Mumbai 400070'),
  ('INOX – Lulu Mall',          'Kochi',     'Lulu International Shopping Mall, Edapally, Kochi 682024'),
  ('Cinepolis – VR Chennai',    'Chennai',   'VR Chennai, Koyambedu, Chennai 600092');

-- screens (PVR Mumbai has 3 screens)
INSERT INTO screens (theatre_id, name, total_seats) VALUES
  (1, 'Screen 1', 200),
  (1, 'Screen 2', 150),
  (1, 'Screen 3', 120),
  (2, 'Audi A',   180),
  (2, 'Audi B',   160),
  (3, 'Hall 1',   220);

-- seats — a small representative subset for Screen 1 (rows A & B, 5 seats each)
INSERT INTO seats (screen_id, row_label, seat_number, seat_type) VALUES
  (1,'A',1,'REGULAR'),(1,'A',2,'REGULAR'),(1,'A',3,'REGULAR'),(1,'A',4,'REGULAR'),(1,'A',5,'REGULAR'),
  (1,'B',1,'PREMIUM'),(1,'B',2,'PREMIUM'),(1,'B',3,'PREMIUM'),(1,'B',4,'PREMIUM'),(1,'B',5,'PREMIUM');

-- shows (screen 1 & 2 at PVR Mumbai on 2024-10-01)
INSERT INTO shows (movie_id, screen_id, show_date, start_time, base_price) VALUES
  (1, 1, '2024-10-01', '10:00:00', 250.00),  -- Kalki — Screen 1, morning
  (1, 1, '2024-10-01', '14:00:00', 300.00),  -- Kalki — Screen 1, afternoon
  (2, 2, '2024-10-01', '11:30:00', 200.00),  -- Stree 2 — Screen 2
  (3, 3, '2024-10-01', '18:00:00', 350.00);  -- Devara — Screen 3

-- show_seats for show 1 (Kalki 10:00 AM, Screen 1, seats A1-A5, B1-B5)
INSERT INTO show_seats (show_id, seat_id, status) VALUES
  (1,1,'AVAILABLE'),(1,2,'AVAILABLE'),(1,3,'AVAILABLE'),(1,4,'AVAILABLE'),(1,5,'AVAILABLE'),
  (1,6,'AVAILABLE'),(1,7,'AVAILABLE'),(1,8,'AVAILABLE'),(1,9,'AVAILABLE'),(1,10,'AVAILABLE');

-- booking (Arjun books seats A1 & A2 for show 1)
INSERT INTO bookings (user_id, show_id, status, total_amount) VALUES
  (1, 1, 'CONFIRMED', 500.00);

-- mark those seats as BOOKED
UPDATE show_seats SET status = 'BOOKED', booking_id = 1
WHERE show_id = 1 AND seat_id IN (1, 2);

-- payment for that booking
INSERT INTO payments (booking_id, amount, status, gateway, external_txn_id) VALUES
  (1, 500.00, 'SUCCESS', 'razorpay', 'rzp_live_abc123XYZ');
