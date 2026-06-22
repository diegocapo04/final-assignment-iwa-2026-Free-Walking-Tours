import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
from db.database import init_db, get_connection

DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "database.db")

os.makedirs(DB_DIR, exist_ok=True)


def reset_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def next_weekday(weekday):
    """Next occurrence of a weekday (0=Monday..6=Sunday) strictly in the future."""
    today = date.today()
    days_ahead = (weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")


def last_weekday(weekday):
    """Most recent past occurrence of a weekday (used for already-happened dates)."""
    today = date.today()
    days_behind = (today.weekday() - weekday) % 7
    if days_behind == 0:
        days_behind = 7
    return (today - timedelta(days=days_behind)).strftime("%Y-%m-%d")


def seed():
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def add_user(first, last, email, password, role):
        cur.execute("""
            INSERT INTO users (first_name, last_name, email, password_hash, role)
            VALUES (?, ?, ?, ?, ?)
        """, (first, last, email, generate_password_hash(password), role))
        return cur.lastrowid

    def add_tour(guide_id, title, meeting_point, duration, language, max_p, description, schedules, stops):
        cur.execute("""
            INSERT INTO tours (guide_id, title, meeting_point, duration_minutes, language, max_participants, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (guide_id, title, meeting_point, duration, language, max_p, description, now))
        tour_id = cur.lastrowid
        for weekday, start_time in schedules:
            cur.execute("INSERT INTO tour_schedules (tour_id, weekday, start_time) VALUES (?, ?, ?)",
                        (tour_id, weekday, start_time))
        for i, stop in enumerate(stops, start=1):
            cur.execute("INSERT INTO tour_stops (tour_id, stop_order, stop_name) VALUES (?, ?, ?)",
                        (tour_id, i, stop))
        return tour_id

    def add_reservation(participant_id, tour_id, tour_date, guests):
        total_people = 1 + len(guests)
        cur.execute("""
            INSERT INTO reservations (participant_id, tour_id, tour_date, total_people, status, created_at, cancelled_at)
            VALUES (?, ?, ?, ?, 'active', ?, NULL)
        """, (participant_id, tour_id, tour_date, total_people, now))
        reservation_id = cur.lastrowid
        for first, last in guests:
            cur.execute("INSERT INTO reservation_guests (reservation_id, first_name, last_name) VALUES (?, ?, ?)",
                        (reservation_id, first, last))
        return reservation_id

    # Admin (single platform administrator)
    add_user("Admin", "User", "admin@arpinowalks.it", "admin12345", "admin")

    # Guides
    guide1 = add_user("Luca", "Bianchi", "luca@arpinowalks.it", "guide12345", "guide")
    guide2 = add_user("Marta", "Verdi", "marta@arpinowalks.it", "guide12345", "guide")

    for lang in ["Italian", "English"]:
        cur.execute("INSERT INTO guide_languages (guide_id, language) VALUES (?, ?)", (guide1, lang))
    for lang in ["Spanish", "English", "German"]:
        cur.execute("INSERT INTO guide_languages (guide_id, language) VALUES (?, ?)", (guide2, lang))

    # Participants
    p1 = add_user("Sara", "Rossi", "sara@arpinowalks.it", "participant12345", "participant")
    p2 = add_user("Marco", "Neri", "marco@arpinowalks.it", "participant12345", "participant")
    p3 = add_user("Giulia", "Conti", "giulia@arpinowalks.it", "participant12345", "participant")

    # Tours
    tour1 = add_tour(
        guide1, "Medieval Arpino Walk", "Piazza Municipio, Arpino", 120, "Italian", 10,
        "Discover the ancient walls and towers of Arpino, birthplace of Cicero.",
        [(5, "10:00"), (6, "10:00")],
        ["Piazza Municipio", "Acropoli di Arpino", "Torre di Cicerone", "Porta Sanguinara", "Museo Civico"],
    )
    tour2 = add_tour(
        guide1, "Cicero's Birthplace Trail", "Fontana di Piazza Municipio, Arpino", 180, "English", 8,
        "Follow the footsteps of the great Roman orator through the historic center.",
        [(6, "15:00")],
        ["Fontana di Piazza Municipio", "Casa di Cicerone", "Mura Ciclopiche", "Arco Romano", "Belvedere del Colle"],
    )
    tour3 = add_tour(
        guide2, "Arpino Street Art Tour", "Stazione di Arpino", 90, "Spanish", 6,
        "A walk among murals and contemporary art spread across the lower town.",
        [(4, "17:00"), (5, "11:00")],
        ["Stazione", "Murale del Borgo", "Vicolo dei Pittori", "Piazzetta dell'Arte"],
    )
    add_tour(
        guide2, "Legends and Night Walk", "Arco a Sesto Acuto, Arpino", 60, "German", 12,
        "An evening stroll through the legends and dark corners of medieval Arpino.",
        [(5, "21:00")],
        ["Arco a Sesto Acuto", "Casa del Fantasma", "Antica Cisterna", "Belvedere Notturno"],
    )

    # Reservations
    # Past date with reservations -> ready for the post-tour report (commission).
    add_reservation(p1, tour1, last_weekday(5), [("Anna", "Bianchi"), ("Paolo", "Verdi")])
    # Future reservations.
    add_reservation(p2, tour1, next_weekday(5), [("Elena", "Rossi")])
    add_reservation(p3, tour2, next_weekday(6), [])
    add_reservation(p1, tour3, next_weekday(4), [("Davide", "Conti")])

    conn.commit()
    cur.close()
    conn.close()


def main():
    reset_database()
    init_db()
    seed()
    print("Database initialized and seeded successfully.")


if __name__ == "__main__":
    main()
