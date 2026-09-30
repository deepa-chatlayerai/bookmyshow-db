"""
Generate BookMyShow DB Design PDF deliverable using ReportLab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "BookMyShow_DB_Design.pdf")

# ── Colour palette ────────────────────────────────────────────────────────────
BRAND     = colors.HexColor("#E63946")   # BMS red
DARK      = colors.HexColor("#1D3557")   # deep navy
MID       = colors.HexColor("#457B9D")   # steel blue
LIGHT_BG  = colors.HexColor("#F1FAEE")   # very light mint
TH_BG     = colors.HexColor("#1D3557")   # table header bg
TH_FG     = colors.white
ROW_ALT   = colors.HexColor("#EBF2FA")
CODE_BG   = colors.HexColor("#1E1E2E")   # dark code block
CODE_FG   = colors.HexColor("#CDD6F4")

# ── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def make_style(name, parent="Normal", **kw):
    s = ParagraphStyle(name, parent=styles[parent], **kw)
    return s

H1 = make_style("H1", "Heading1",
    fontSize=22, textColor=DARK, spaceAfter=6, spaceBefore=18,
    fontName="Helvetica-Bold")

H2 = make_style("H2", "Heading2",
    fontSize=15, textColor=BRAND, spaceAfter=4, spaceBefore=14,
    fontName="Helvetica-Bold")

H3 = make_style("H3", "Heading3",
    fontSize=12, textColor=MID, spaceAfter=3, spaceBefore=10,
    fontName="Helvetica-Bold")

BODY = make_style("Body", "Normal",
    fontSize=9.5, leading=14, textColor=colors.HexColor("#2d2d2d"),
    spaceAfter=4)

CAPTION = make_style("Caption", "Normal",
    fontSize=8, leading=11, textColor=colors.HexColor("#555555"),
    spaceAfter=2, fontName="Helvetica-Oblique")

CODE = make_style("Code", "Normal",
    fontSize=7.8, leading=12, fontName="Courier",
    textColor=CODE_FG, backColor=CODE_BG,
    leftIndent=8, rightIndent=8,
    spaceBefore=4, spaceAfter=4)

NOTE = make_style("Note", "Normal",
    fontSize=8.5, leading=12, textColor=colors.HexColor("#444"),
    leftIndent=12, rightIndent=12, spaceBefore=2, spaceAfter=6,
    fontName="Helvetica-Oblique")

# ── Helpers ───────────────────────────────────────────────────────────────────
def hr():
    return HRFlowable(width="100%", thickness=0.5,
                      color=colors.HexColor("#cccccc"), spaceAfter=6)

def h1(txt):  return Paragraph(txt, H1)
def h2(txt):  return Paragraph(txt, H2)
def h3(txt):  return Paragraph(txt, H3)
def body(txt): return Paragraph(txt, BODY)
def note(txt): return Paragraph(f"<i>{txt}</i>", NOTE)
def sp(h=4):  return Spacer(1, h)

TH_STYLE = ParagraphStyle("TH", fontName="Helvetica-Bold",
    fontSize=8.5, textColor=TH_FG, leading=11)
TD_STYLE = ParagraphStyle("TD", fontName="Helvetica",
    fontSize=8, textColor=colors.HexColor("#1a1a1a"), leading=11)
TD_CODE  = ParagraphStyle("TDCode", fontName="Courier",
    fontSize=7.5, textColor=colors.HexColor("#1a1a1a"), leading=11)

def tbl_header(*cols):
    return [Paragraph(c, TH_STYLE) for c in cols]

def tbl_row(*cols, code_cols=None):
    code_cols = code_cols or []
    return [
        Paragraph(c, TD_CODE if i in code_cols else TD_STYLE)
        for i, c in enumerate(cols)
    ]

BASE_TBL = TableStyle([
    ("BACKGROUND",  (0,0), (-1,0),  TH_BG),
    ("TEXTCOLOR",   (0,0), (-1,0),  TH_FG),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, ROW_ALT]),
    ("GRID",        (0,0), (-1,-1), 0.35, colors.HexColor("#c8c8c8")),
    ("TOPPADDING",  (0,0), (-1,-1), 4),
    ("BOTTOMPADDING",(0,0),(-1,-1), 4),
    ("LEFTPADDING", (0,0), (-1,-1), 5),
    ("RIGHTPADDING",(0,0), (-1,-1), 5),
    ("VALIGN",      (0,0), (-1,-1), "TOP"),
])

def make_table(rows, col_widths):
    t = Table(rows, colWidths=col_widths, repeatRows=1)
    t.setStyle(BASE_TBL)
    return t

def code_block(sql_text):
    """Render a code block as individual row-per-line table for page-safe splitting."""
    lines = sql_text.strip().splitlines()
    rows = []
    for line in lines:
        safe = (line
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))
        rows.append([Paragraph(safe if safe.strip() else "&nbsp;", CODE)])
    t = Table(rows, colWidths=[155*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), CODE_BG),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING",   (0,0), (-1,-1), 1),
        ("BOTTOMPADDING",(0,0), (-1,-1), 1),
    ]))
    return t

# ── Cover page ────────────────────────────────────────────────────────────────
def cover():
    elems = []
    elems.append(Spacer(1, 55*mm))
    title_style = ParagraphStyle("Cover", fontName="Helvetica-Bold",
        fontSize=30, textColor=DARK, alignment=TA_CENTER, leading=36)
    sub_style = ParagraphStyle("CoverSub", fontName="Helvetica",
        fontSize=13, textColor=MID, alignment=TA_CENTER, spaceBefore=6)
    tag_style = ParagraphStyle("CoverTag", fontName="Helvetica-Oblique",
        fontSize=10, textColor=colors.HexColor("#888"), alignment=TA_CENTER)

    elems.append(Paragraph("BookMyShow", ParagraphStyle("Red", fontName="Helvetica-Bold",
        fontSize=36, textColor=BRAND, alignment=TA_CENTER)))
    elems.append(Spacer(1, 4*mm))
    elems.append(Paragraph("Ticketing Backend — Database Design", title_style))
    elems.append(Spacer(1, 6*mm))
    elems.append(HRFlowable(width="60%", thickness=1.5, color=BRAND,
                             hAlign="CENTER", spaceAfter=6))
    elems.append(Spacer(1, 4*mm))
    elems.append(Paragraph("P1: Schema · Normalization · Concurrency Strategy", sub_style))
    elems.append(Paragraph("P2: Show Listing Query", sub_style))
    elems.append(Spacer(1, 20*mm))
    elems.append(Paragraph("MySQL • InnoDB • Row-level Locking • Idempotent Webhooks", tag_style))
    elems.append(PageBreak())
    return elems

# ── Section: Entities & Attributes ───────────────────────────────────────────
def section_entities():
    W = 155*mm
    elems = []
    elems += [h1("1. Entities and Attributes"), hr(), sp(4)]

    entities = [
        {
            "name": "users",
            "desc": "Platform users who make bookings.",
            "cols": [("id","BIGINT UNSIGNED","PK, AUTO_INCREMENT"),
                     ("name","VARCHAR(120)","NOT NULL"),
                     ("email","VARCHAR(255)","NOT NULL, UNIQUE"),
                     ("phone","VARCHAR(15)","NOT NULL, UNIQUE"),
                     ("created_at","DATETIME","NOT NULL, DEFAULT NOW()")],
        },
        {
            "name": "movies",
            "desc": "Movie catalogue — language, genre, duration.",
            "cols": [("id","BIGINT UNSIGNED","PK, AUTO_INCREMENT"),
                     ("title","VARCHAR(255)","NOT NULL"),
                     ("duration_mins","SMALLINT UNSIGNED","NOT NULL"),
                     ("language","VARCHAR(50)","NOT NULL"),
                     ("genre","VARCHAR(80)","NOT NULL"),
                     ("rating","CHAR(5)","nullable (e.g. U/A, A)"),
                     ("release_date","DATE","NOT NULL")],
        },
        {
            "name": "theatres",
            "desc": "Physical cinema locations.",
            "cols": [("id","BIGINT UNSIGNED","PK, AUTO_INCREMENT"),
                     ("name","VARCHAR(255)","NOT NULL"),
                     ("city","VARCHAR(100)","NOT NULL"),
                     ("address","TEXT","NOT NULL")],
        },
        {
            "name": "screens",
            "desc": "Auditoriums inside a theatre.",
            "cols": [("id","BIGINT UNSIGNED","PK, AUTO_INCREMENT"),
                     ("theatre_id","BIGINT UNSIGNED","FK → theatres.id"),
                     ("name","VARCHAR(60)","NOT NULL"),
                     ("total_seats","SMALLINT UNSIGNED","NOT NULL"),
                     ("—","—","UNIQUE (theatre_id, name)")],
        },
        {
            "name": "seats",
            "desc": "Fixed physical seats in a screen. Created once, never deleted.",
            "cols": [("id","BIGINT UNSIGNED","PK, AUTO_INCREMENT"),
                     ("screen_id","BIGINT UNSIGNED","FK → screens.id"),
                     ("row_label","CHAR(3)","NOT NULL (e.g. A, B, AA)"),
                     ("seat_number","TINYINT UNSIGNED","NOT NULL, 1-based"),
                     ("seat_type","ENUM","REGULAR / PREMIUM / RECLINER"),
                     ("—","—","UNIQUE (screen_id, row_label, seat_number)")],
        },
        {
            "name": "shows",
            "desc": "One screening of a movie on a specific screen at a date/time.",
            "cols": [("id","BIGINT UNSIGNED","PK, AUTO_INCREMENT"),
                     ("movie_id","BIGINT UNSIGNED","FK → movies.id"),
                     ("screen_id","BIGINT UNSIGNED","FK → screens.id"),
                     ("show_date","DATE","NOT NULL"),
                     ("start_time","TIME","NOT NULL"),
                     ("base_price","DECIMAL(8,2)","NOT NULL"),
                     ("—","—","UNIQUE (screen_id, show_date, start_time)")],
        },
        {
            "name": "show_seats",
            "desc": "Per-show availability state for every seat. Core of concurrency control.",
            "cols": [("id","BIGINT UNSIGNED","PK, AUTO_INCREMENT"),
                     ("show_id","BIGINT UNSIGNED","FK → shows.id"),
                     ("seat_id","BIGINT UNSIGNED","FK → seats.id"),
                     ("status","ENUM","AVAILABLE / HELD / BOOKED"),
                     ("hold_expires_at","DATETIME","nullable — set when status=HELD"),
                     ("booking_id","BIGINT UNSIGNED","FK → bookings.id, nullable"),
                     ("version","INT UNSIGNED","optimistic lock counter"),
                     ("—","—","UNIQUE (show_id, seat_id)")],
        },
        {
            "name": "bookings",
            "desc": "A user's purchase attempt for one or more seats at a show.",
            "cols": [("id","BIGINT UNSIGNED","PK, AUTO_INCREMENT"),
                     ("user_id","BIGINT UNSIGNED","FK → users.id"),
                     ("show_id","BIGINT UNSIGNED","FK → shows.id"),
                     ("status","ENUM","PENDING / CONFIRMED / CANCELLED / FAILED"),
                     ("total_amount","DECIMAL(10,2)","NOT NULL"),
                     ("created_at","DATETIME","NOT NULL"),
                     ("updated_at","DATETIME","NOT NULL, ON UPDATE CURRENT_TIMESTAMP")],
        },
        {
            "name": "payments",
            "desc": "Payment records. Idempotency enforced via UNIQUE external_txn_id.",
            "cols": [("id","BIGINT UNSIGNED","PK, AUTO_INCREMENT"),
                     ("booking_id","BIGINT UNSIGNED","FK → bookings.id"),
                     ("amount","DECIMAL(10,2)","NOT NULL"),
                     ("status","ENUM","PENDING / SUCCESS / FAILED / REFUNDED"),
                     ("gateway","VARCHAR(60)","NOT NULL (e.g. razorpay, stripe)"),
                     ("external_txn_id","VARCHAR(255)","NOT NULL, UNIQUE"),
                     ("payload","JSON","nullable — raw webhook body for audit"),
                     ("created_at","DATETIME","NOT NULL"),
                     ("updated_at","DATETIME","NOT NULL, ON UPDATE")],
        },
    ]

    col_w = [W*0.22, W*0.28, W*0.50]
    for ent in entities:
        rows = [tbl_header("Column", "Type", "Constraints")]
        for col, typ, con in ent["cols"]:
            rows.append(tbl_row(col, typ, con, code_cols=[0,1]))
        elems += [
            KeepTogether([
                h3(f"  {ent['name']}"),
                note(ent["desc"]),
                make_table(rows, col_w),
                sp(8),
            ])
        ]
    return elems

# ── Section: Sample Rows ──────────────────────────────────────────────────────
def section_samples():
    W = 155*mm
    elems = [PageBreak(), h1("2. Sample Rows"), hr(), sp(4)]

    # users
    elems.append(h3("  users"))
    rows = [tbl_header("id","name","email","phone")]
    rows += [
        tbl_row("1","Arjun Mehta","arjun@example.com","9876543210"),
        tbl_row("2","Priya Sharma","priya@example.com","9123456780"),
        tbl_row("3","Rohan Kapoor","rohan@example.com","9988776655"),
    ]
    elems += [make_table(rows, [W*0.07, W*0.23, W*0.40, W*0.30]), sp(8)]

    # movies
    elems.append(h3("  movies"))
    rows = [tbl_header("id","title","duration","language","genre","rating")]
    rows += [
        tbl_row("1","Kalki 2898 AD","180 min","Telugu","Sci-Fi / Action","U/A"),
        tbl_row("2","Stree 2","135 min","Hindi","Horror Comedy","U/A"),
        tbl_row("3","Devara: Part 1","166 min","Telugu","Action Drama","U/A"),
    ]
    elems += [make_table(rows, [W*0.05, W*0.28, W*0.12, W*0.13, W*0.25, W*0.10]), sp(8)]

    # theatres
    elems.append(h3("  theatres"))
    rows = [tbl_header("id","name","city")]
    rows += [
        tbl_row("1","PVR Cinemas – Phoenix Mall","Mumbai"),
        tbl_row("2","INOX – Lulu Mall","Kochi"),
        tbl_row("3","Cinepolis – VR Chennai","Chennai"),
    ]
    elems += [make_table(rows, [W*0.07, W*0.55, W*0.38]), sp(8)]

    # screens
    elems.append(h3("  screens"))
    rows = [tbl_header("id","theatre_id","name","total_seats")]
    rows += [
        tbl_row("1","1","Screen 1","200"),
        tbl_row("2","1","Screen 2","150"),
        tbl_row("3","1","Screen 3","120"),
        tbl_row("4","2","Audi A","180"),
        tbl_row("5","2","Audi B","160"),
    ]
    elems += [make_table(rows, [W*0.08, W*0.18, W*0.40, W*0.20]), sp(8)]

    # shows
    elems.append(h3("  shows  (PVR Mumbai, 2024-10-01)"))
    rows = [tbl_header("id","movie","screen","show_date","start_time","base_price")]
    rows += [
        tbl_row("1","Kalki 2898 AD","Screen 1","2024-10-01","10:00","₹250"),
        tbl_row("2","Kalki 2898 AD","Screen 1","2024-10-01","14:00","₹300"),
        tbl_row("3","Stree 2","Screen 2","2024-10-01","11:30","₹200"),
        tbl_row("4","Devara: Part 1","Screen 3","2024-10-01","18:00","₹350"),
    ]
    elems += [make_table(rows, [W*0.05,W*0.28,W*0.15,W*0.17,W*0.15,W*0.14]), sp(8)]

    # show_seats
    elems.append(h3("  show_seats  (show_id = 1)"))
    rows = [tbl_header("show_id","seat_id","status","hold_expires_at","booking_id")]
    rows += [
        tbl_row("1","1","BOOKED","NULL","1"),
        tbl_row("1","2","BOOKED","NULL","1"),
        tbl_row("1","3","AVAILABLE","NULL","NULL"),
        tbl_row("1","4","HELD","2024-10-01 10:15:00","NULL"),
    ]
    elems += [make_table(rows, [W*0.14,W*0.13,W*0.17,W*0.33,W*0.17]), sp(8)]

    # bookings
    elems.append(h3("  bookings"))
    rows = [tbl_header("id","user_id","show_id","status","total_amount")]
    rows += [
        tbl_row("1","1","1","CONFIRMED","500.00"),
    ]
    elems += [make_table(rows, [W*0.08,W*0.15,W*0.15,W*0.27,W*0.20]), sp(8)]

    # payments
    elems.append(h3("  payments"))
    rows = [tbl_header("id","booking_id","amount","status","gateway","external_txn_id")]
    rows += [
        tbl_row("1","1","500.00","SUCCESS","razorpay","rzp_live_abc123XYZ"),
    ]
    elems += [make_table(rows, [W*0.05,W*0.14,W*0.12,W*0.15,W*0.16,W*0.32]), sp(8)]

    return elems

# ── Section: P1 — CREATE TABLE SQL ───────────────────────────────────────────
def section_schema_sql():
    elems = [PageBreak(), h1("3. P1 — CREATE TABLE SQL  (schema.sql)"), hr(), sp(4)]
    elems.append(note(
        "All statements are directly executable on MySQL 8.0+. "
        "Run schema.sql first, then sample_data.sql."
    ))
    elems.append(sp(6))

    sql = """\
-- BookMyShow Ticketing Backend — MySQL Schema

CREATE TABLE users (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(120)  NOT NULL,
    email       VARCHAR(255)  NOT NULL,
    phone       VARCHAR(15)   NOT NULL,
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_email (email),
    UNIQUE KEY uq_users_phone (phone)
);

CREATE TABLE movies (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title           VARCHAR(255)       NOT NULL,
    duration_mins   SMALLINT UNSIGNED  NOT NULL,
    language        VARCHAR(50)        NOT NULL,
    genre           VARCHAR(80)        NOT NULL,
    rating          CHAR(5),
    release_date    DATE               NOT NULL
);

CREATE TABLE theatres (
    id      BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(255) NOT NULL,
    city    VARCHAR(100) NOT NULL,
    address TEXT         NOT NULL
);

CREATE TABLE screens (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    theatre_id  BIGINT UNSIGNED   NOT NULL,
    name        VARCHAR(60)       NOT NULL,
    total_seats SMALLINT UNSIGNED NOT NULL,
    CONSTRAINT fk_screens_theatre FOREIGN KEY (theatre_id)
        REFERENCES theatres (id) ON DELETE CASCADE,
    UNIQUE KEY uq_screen_name_per_theatre (theatre_id, name)
);

CREATE TABLE seats (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    screen_id   BIGINT UNSIGNED  NOT NULL,
    row_label   CHAR(3)          NOT NULL,
    seat_number TINYINT UNSIGNED NOT NULL,
    seat_type   ENUM('REGULAR','PREMIUM','RECLINER')
                NOT NULL DEFAULT 'REGULAR',
    CONSTRAINT fk_seats_screen FOREIGN KEY (screen_id)
        REFERENCES screens (id) ON DELETE CASCADE,
    UNIQUE KEY uq_seat_position (screen_id, row_label, seat_number)
);

CREATE TABLE shows (
    id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    movie_id    BIGINT UNSIGNED NOT NULL,
    screen_id   BIGINT UNSIGNED NOT NULL,
    show_date   DATE            NOT NULL,
    start_time  TIME            NOT NULL,
    base_price  DECIMAL(8,2)    NOT NULL,
    CONSTRAINT fk_shows_movie  FOREIGN KEY (movie_id)
        REFERENCES movies  (id),
    CONSTRAINT fk_shows_screen FOREIGN KEY (screen_id)
        REFERENCES screens (id),
    UNIQUE KEY uq_show_slot (screen_id, show_date, start_time),
    INDEX idx_shows_date_screen (show_date, screen_id)
);

CREATE TABLE show_seats (
    id              BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    show_id         BIGINT UNSIGNED NOT NULL,
    seat_id         BIGINT UNSIGNED NOT NULL,
    status          ENUM('AVAILABLE','HELD','BOOKED')
                    NOT NULL DEFAULT 'AVAILABLE',
    hold_expires_at DATETIME        NULL,
    booking_id      BIGINT UNSIGNED NULL,
    version         INT UNSIGNED    NOT NULL DEFAULT 0,
    CONSTRAINT fk_ss_show FOREIGN KEY (show_id) REFERENCES shows (id),
    CONSTRAINT fk_ss_seat FOREIGN KEY (seat_id) REFERENCES seats (id),
    UNIQUE KEY uq_show_seat (show_id, seat_id),
    INDEX idx_ss_show_status (show_id, status),
    INDEX idx_ss_expires (hold_expires_at)
);

CREATE TABLE bookings (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id      BIGINT UNSIGNED NOT NULL,
    show_id      BIGINT UNSIGNED NOT NULL,
    status       ENUM('PENDING','CONFIRMED','CANCELLED','FAILED')
                 NOT NULL DEFAULT 'PENDING',
    total_amount DECIMAL(10,2)   NOT NULL,
    created_at   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                 ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_bookings_user FOREIGN KEY (user_id)
        REFERENCES users (id),
    CONSTRAINT fk_bookings_show FOREIGN KEY (show_id)
        REFERENCES shows (id),
    INDEX idx_bookings_user (user_id),
    INDEX idx_bookings_show (show_id)
);

ALTER TABLE show_seats
    ADD CONSTRAINT fk_ss_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (id) ON DELETE SET NULL;

CREATE TABLE payments (
    id               BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    booking_id       BIGINT UNSIGNED NOT NULL,
    amount           DECIMAL(10,2)   NOT NULL,
    status           ENUM('PENDING','SUCCESS','FAILED','REFUNDED')
                     NOT NULL DEFAULT 'PENDING',
    gateway          VARCHAR(60)     NOT NULL,
    external_txn_id  VARCHAR(255)    NOT NULL,
    payload          JSON            NULL,
    created_at       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP
                     ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_payments_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (id),
    UNIQUE KEY uq_external_txn (external_txn_id)
);"""

    elems.append(code_block(sql))
    return elems

# ── Section: Sample INSERT SQL ────────────────────────────────────────────────
def section_sample_sql():
    elems = [PageBreak(), h1("4. P1 — Sample INSERT Statements  (sample_data.sql)"), hr(), sp(4)]

    sql = """\
-- users
INSERT INTO users (name, email, phone) VALUES
  ('Arjun Mehta',  'arjun@example.com', '9876543210'),
  ('Priya Sharma', 'priya@example.com', '9123456780'),
  ('Rohan Kapoor', 'rohan@example.com', '9988776655');

-- movies
INSERT INTO movies (title, duration_mins, language, genre, rating, release_date) VALUES
  ('Kalki 2898 AD',   180, 'Telugu', 'Sci-Fi / Action', 'U/A', '2024-06-27'),
  ('Stree 2',         135, 'Hindi',  'Horror Comedy',   'U/A', '2024-08-15'),
  ('Devara: Part 1',  166, 'Telugu', 'Action Drama',    'U/A', '2024-09-27');

-- theatres
INSERT INTO theatres (name, city, address) VALUES
  ('PVR Cinemas – Phoenix Mall', 'Mumbai',  'LBS Marg, Kurla West, Mumbai 400070'),
  ('INOX – Lulu Mall',           'Kochi',   'Lulu Mall, Edapally, Kochi 682024'),
  ('Cinepolis – VR Chennai',     'Chennai', 'VR Chennai, Koyambedu, Chennai 600092');

-- screens
INSERT INTO screens (theatre_id, name, total_seats) VALUES
  (1,'Screen 1',200),(1,'Screen 2',150),(1,'Screen 3',120),
  (2,'Audi A',180),(2,'Audi B',160),(3,'Hall 1',220);

-- seats (rows A & B, 5 seats each, in Screen 1)
INSERT INTO seats (screen_id, row_label, seat_number, seat_type) VALUES
  (1,'A',1,'REGULAR'),(1,'A',2,'REGULAR'),(1,'A',3,'REGULAR'),
  (1,'A',4,'REGULAR'),(1,'A',5,'REGULAR'),
  (1,'B',1,'PREMIUM'),(1,'B',2,'PREMIUM'),(1,'B',3,'PREMIUM'),
  (1,'B',4,'PREMIUM'),(1,'B',5,'PREMIUM');

-- shows
INSERT INTO shows (movie_id, screen_id, show_date, start_time, base_price) VALUES
  (1, 1, '2024-10-01', '10:00:00', 250.00),
  (1, 1, '2024-10-01', '14:00:00', 300.00),
  (2, 2, '2024-10-01', '11:30:00', 200.00),
  (3, 3, '2024-10-01', '18:00:00', 350.00);

-- show_seats for show 1
INSERT INTO show_seats (show_id, seat_id, status) VALUES
  (1,1,'AVAILABLE'),(1,2,'AVAILABLE'),(1,3,'AVAILABLE'),
  (1,4,'AVAILABLE'),(1,5,'AVAILABLE'),(1,6,'AVAILABLE'),
  (1,7,'AVAILABLE'),(1,8,'AVAILABLE'),(1,9,'AVAILABLE'),(1,10,'AVAILABLE');

-- booking + seat update + payment
INSERT INTO bookings (user_id, show_id, status, total_amount)
  VALUES (1, 1, 'CONFIRMED', 500.00);

UPDATE show_seats SET status='BOOKED', booking_id=1
WHERE show_id=1 AND seat_id IN (1,2);

INSERT INTO payments (booking_id, amount, status, gateway, external_txn_id)
  VALUES (1, 500.00, 'SUCCESS', 'razorpay', 'rzp_live_abc123XYZ');"""

    elems.append(code_block(sql))
    return elems

# ── Section: Normalization ────────────────────────────────────────────────────
def section_normalization():
    elems = [PageBreak(), h1("5. Normalization"), hr(), sp(4)]

    norms = [
        ("1NF — First Normal Form",
         "All columns hold atomic, single-valued data. There are no repeating groups "
         "or arrays. For example, a booking's seats are stored as individual rows in "
         "show_seats, not as a comma-separated list inside the bookings row."),
        ("2NF — Second Normal Form",
         "Every non-key column depends on the entire primary key. All tables use a "
         "single-column surrogate PK (id), eliminating the possibility of partial "
         "dependency. In show_seats, status and hold_expires_at depend on the full "
         "(show_id, seat_id) combination enforced as a UNIQUE key — not on either "
         "column alone."),
        ("3NF — Third Normal Form",
         "No transitive dependencies exist. Theatre city and address live only in "
         "theatres — they are not duplicated in screens. Show base_price is a property "
         "of the show, not of the seat; per-seat pricing differences are handled via "
         "seats.seat_type, keeping show_seats free of derived data."),
        ("BCNF — Boyce–Codd Normal Form",
         "Every determinant is a candidate key. In show_seats the UNIQUE (show_id, "
         "seat_id) constraint makes this pair a candidate key; all other columns are "
         "determined solely by it. In shows the UNIQUE (screen_id, show_date, "
         "start_time) constraint is the natural candidate key — a screen can only "
         "run one movie at a time — and all non-key attributes depend on it."),
    ]

    W = 155*mm
    rows = [tbl_header("Normal Form", "Guarantee achieved")]
    for nf, desc in norms:
        rows.append([
            Paragraph(nf, ParagraphStyle("NF", fontName="Helvetica-Bold",
                fontSize=8.5, textColor=DARK, leading=12)),
            Paragraph(desc, TD_STYLE),
        ])
    t = Table(rows, colWidths=[W*0.28, W*0.72], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  TH_BG),
        ("TEXTCOLOR",   (0,0), (-1,0),  TH_FG),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, ROW_ALT]),
        ("GRID",        (0,0), (-1,-1), 0.35, colors.HexColor("#c8c8c8")),
        ("TOPPADDING",  (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING",(0,0), (-1,-1), 6),
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
    ]))
    elems.append(t)
    return elems

# ── Section: Concurrency ──────────────────────────────────────────────────────
def section_concurrency():
    elems = [PageBreak(), h1("6. Concurrency & Locking Strategy"), hr(), sp(4)]

    elems.append(h2("The Problem"))
    elems.append(body(
        "Thousands of users may try to book the same seat simultaneously. Without "
        "protection, two transactions can both read a seat as AVAILABLE and both "
        "commit a BOOKED record — resulting in a double-booking."
    ))
    elems.append(sp(6))

    elems.append(h2("Approach: Pessimistic Row-level Locking"))
    elems.append(body(
        "When a user selects seats, the application opens a transaction and issues "
        "SELECT ... FOR UPDATE on the target show_seats rows. InnoDB acquires "
        "exclusive row locks. Any concurrent transaction trying to lock the same "
        "rows blocks until the first commits or rolls back."
    ))
    elems.append(sp(4))

    hold_sql = """\
START TRANSACTION;

-- Acquire exclusive locks on the requested seats
SELECT id, status
FROM   show_seats
WHERE  show_id = 1
  AND  seat_id IN (3, 4)
  AND  status  = 'AVAILABLE'
FOR UPDATE;

-- Proceed only if rows_returned == seats_requested.
-- Transition to HELD with a 10-minute expiry.
UPDATE show_seats
SET    status          = 'HELD',
       hold_expires_at = DATE_ADD(NOW(), INTERVAL 10 MINUTE),
       booking_id      = :new_booking_id
WHERE  show_id = 1
  AND  seat_id IN (3, 4)
  AND  status  = 'AVAILABLE';

-- If rows_affected < seats_requested → ROLLBACK
COMMIT;"""
    elems.append(code_block(hold_sql))
    elems.append(note(
        "If a second transaction arrives while the first holds the lock, it blocks. "
        "After the first commits (status = HELD), the second re-evaluates and finds "
        "0 AVAILABLE rows — it rolls back cleanly. No double-booking possible."
    ))
    elems.append(sp(8))

    elems.append(h2("Hold Expiry — Releasing Stale Holds"))
    elems.append(body(
        "A background job (cron every minute, or Redis TTL keyspace notification) "
        "releases seats whose hold has timed out:"
    ))
    elems.append(sp(4))
    expiry_sql = """\
UPDATE show_seats
SET    status          = 'AVAILABLE',
       hold_expires_at = NULL,
       booking_id      = NULL
WHERE  status          = 'HELD'
  AND  hold_expires_at < NOW();"""
    elems.append(code_block(expiry_sql))
    elems.append(note(
        "INDEX idx_ss_expires (hold_expires_at) makes this sweep O(expired rows), "
        "not O(all rows), even at millions of show_seats records."
    ))
    elems.append(sp(8))

    elems.append(h2("Idempotent Payment Webhooks"))
    elems.append(body(
        "payments.external_txn_id carries a UNIQUE constraint. "
        "The webhook handler uses INSERT ... ON DUPLICATE KEY UPDATE, "
        "so a retried webhook from the payment gateway is safely absorbed:"
    ))
    elems.append(sp(4))
    webhook_sql = """\
INSERT INTO payments
    (booking_id, amount, status, gateway, external_txn_id, payload)
VALUES
    (:booking_id, :amount, 'SUCCESS', 'razorpay', :txn_id, :raw_json)
ON DUPLICATE KEY UPDATE
    status     = VALUES(status),
    payload    = VALUES(payload),
    updated_at = NOW();"""
    elems.append(code_block(webhook_sql))
    elems.append(sp(8))

    elems.append(h2("Index Strategy"))
    W = 155*mm
    rows = [tbl_header("Index", "Table", "Purpose")]
    idx = [
        ("idx_shows_date_screen","shows","P2 query — filter by date + screen (theatre join)"),
        ("idx_ss_show_status","show_seats","Count available seats per show efficiently"),
        ("idx_ss_expires","show_seats","Hold-expiry sweep — targets only HELD rows"),
        ("idx_bookings_user","bookings","Fetch a user's booking history"),
        ("uq_show_seat","show_seats","Enforce one status row per (show, seat)"),
        ("uq_external_txn","payments","Idempotency guarantee for payment webhooks"),
    ]
    for name, tbl, purpose in idx:
        rows.append(tbl_row(name, tbl, purpose, code_cols=[0,1]))
    elems.append(make_table(rows, [W*0.32, W*0.20, W*0.48]))
    return elems

# ── Section: P2 Query ─────────────────────────────────────────────────────────
def section_p2():
    elems = [PageBreak(), h1("7. P2 — List Shows by Date & Theatre"), hr(), sp(4)]

    elems.append(body(
        "Returns all shows running at a given theatre on a given date, "
        "including movie details, screen name, start/end times, price, "
        "and live available seat count."
    ))
    elems.append(sp(6))

    sql = """\
-- P2: List all shows on a given date at a given theatre
--
-- Replace the WHERE clause values before running:
--   show_date = '2024-10-01'   ← your target date
--   t.id      = 1              ← your theatre_id

SELECT
    m.title                                        AS movie_title,
    m.language,
    m.genre,
    sc.name                                        AS screen_name,
    sh.show_date,
    sh.start_time,
    ADDTIME(sh.start_time,
            SEC_TO_TIME(m.duration_mins * 60))     AS end_time,
    sh.base_price,
    COUNT(ss.id)                                   AS total_seats,
    SUM(ss.status = 'AVAILABLE')                   AS available_seats
FROM shows       sh
JOIN movies      m   ON m.id  = sh.movie_id
JOIN screens     sc  ON sc.id = sh.screen_id
JOIN theatres    t   ON t.id  = sc.theatre_id
LEFT JOIN show_seats ss ON ss.show_id = sh.id
WHERE sh.show_date = '2024-10-01'
  AND t.id         = 1
GROUP BY
    sh.id, m.title, m.language, m.genre,
    sc.name, sh.show_date, sh.start_time,
    m.duration_mins, sh.base_price
ORDER BY
    sh.start_time;"""

    elems.append(code_block(sql))
    elems.append(sp(8))

    elems.append(h2("Expected Output (sample data)"))
    W = 155*mm
    rows = [tbl_header("movie_title","language","screen","start","end","price","avail")]
    rows += [
        tbl_row("Stree 2","Hindi","Screen 2","11:30","13:45","200.00","10"),
        tbl_row("Kalki 2898 AD","Telugu","Screen 1","10:00","13:00","250.00","8"),
        tbl_row("Kalki 2898 AD","Telugu","Screen 1","14:00","17:00","300.00","10"),
        tbl_row("Devara: Part 1","Telugu","Screen 3","18:00","20:46","350.00","10"),
    ]
    elems.append(make_table(rows,
        [W*0.22, W*0.10, W*0.13, W*0.10, W*0.10, W*0.12, W*0.09]))

    elems.append(sp(8))
    elems.append(h2("Why this query is efficient"))
    bullets = [
        "idx_shows_date_screen (show_date, screen_id) on the shows table lets MySQL "
        "seek directly to the target date without a full scan.",
        "The theatre JOIN on screens.theatre_id adds only the theatre filter; "
        "theatre_id is a FK with an implicit index.",
        "LEFT JOIN show_seats with a conditional SUM counts available seats in one "
        "pass — no correlated subquery needed.",
    ]
    for b in bullets:
        elems.append(body(f"• {b}"))

    return elems

# ── Build PDF ─────────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=18*mm,  bottomMargin=18*mm,
        title="BookMyShow DB Design",
        author="deepa-chatlayerai",
        subject="P1 & P2 Assignment Submission",
    )

    story = []
    story += cover()
    story += section_entities()
    story += section_samples()
    story += section_schema_sql()
    story += section_sample_sql()
    story += section_normalization()
    story += section_concurrency()
    story += section_p2()

    # page numbers
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawRightString(
            A4[0] - 20*mm,
            12*mm,
            f"BookMyShow DB Design  ·  Page {doc.page}"
        )
        canvas.drawString(20*mm, 12*mm, "Confidential — Assignment Submission")
        canvas.restoreState()

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"✓  PDF written to: {OUTPUT}")

if __name__ == "__main__":
    build()
