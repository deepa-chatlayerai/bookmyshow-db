-- ============================================================
-- P2 — List all shows on a given date at a given theatre,
--       along with their show timings.
--
-- Parameters (replace before running):
--   :given_date     e.g. '2024-10-01'
--   :theatre_id     e.g. 1
-- ============================================================

SELECT
    m.title                                             AS movie_title,
    m.language,
    m.genre,
    sc.name                                             AS screen_name,
    sh.show_date,
    sh.start_time,
    ADDTIME(sh.start_time,
            SEC_TO_TIME(m.duration_mins * 60))          AS end_time,
    sh.base_price,
    COUNT(ss.id)                                        AS total_seats,
    SUM(ss.status = 'AVAILABLE')                        AS available_seats
FROM shows       sh
JOIN movies      m   ON m.id  = sh.movie_id
JOIN screens     sc  ON sc.id = sh.screen_id
JOIN theatres    t   ON t.id  = sc.theatre_id
LEFT JOIN show_seats ss ON ss.show_id = sh.id
WHERE sh.show_date = '2024-10-01'   -- replace with :given_date
  AND t.id         = 1              -- replace with :theatre_id
GROUP BY
    sh.id, m.title, m.language, m.genre,
    sc.name, sh.show_date, sh.start_time, m.duration_mins, sh.base_price
ORDER BY
    sh.start_time;
