PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('participant', 'guide', 'admin'))
);

CREATE TABLE IF NOT EXISTS guide_languages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guide_id INTEGER NOT NULL,
    language TEXT NOT NULL CHECK(language IN ('Italian', 'English', 'Spanish', 'Portuguese', 'German')),
    UNIQUE(guide_id, language),
    FOREIGN KEY (guide_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guide_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    meeting_point TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL CHECK(duration_minutes > 0),
    language TEXT NOT NULL CHECK(language IN ('Italian', 'English', 'Spanish', 'Portuguese', 'German')),
    max_participants INTEGER NOT NULL CHECK(max_participants > 0),
    description TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (guide_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tour_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    weekday INTEGER NOT NULL CHECK(weekday BETWEEN 0 AND 6),
    start_time TEXT NOT NULL,
    UNIQUE(tour_id, weekday),
    FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tour_stops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    stop_order INTEGER NOT NULL CHECK(stop_order > 0),
    stop_name TEXT NOT NULL,
    UNIQUE(tour_id, stop_order),
    FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tour_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    photo_order INTEGER NOT NULL CHECK(photo_order BETWEEN 1 AND 5),
    UNIQUE(tour_id, photo_order),
    FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER NOT NULL,
    tour_id INTEGER NOT NULL,
    tour_date TEXT NOT NULL,
    total_people INTEGER NOT NULL CHECK(total_people BETWEEN 1 AND 4),
    status TEXT NOT NULL CHECK(status IN ('active', 'cancelled')) DEFAULT 'active',
    created_at TEXT NOT NULL,
    cancelled_at TEXT,
    FOREIGN KEY (participant_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reservation_guests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tour_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour_id INTEGER NOT NULL,
    tour_date TEXT NOT NULL,
    actual_attendees INTEGER NOT NULL CHECK(actual_attendees >= 0),
    evidence_photo_path TEXT NOT NULL,
    submitted_at TEXT NOT NULL,
    UNIQUE(tour_id, tour_date),
    FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE
);