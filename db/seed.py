import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from werkzeug.security import generate_password_hash
from datetime import datetime
from db.database import init_db, get_connection

DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "database.db")

os.makedirs(DB_DIR, exist_ok=True)


def reset_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def seed():
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Users
    cur.execute("""
        INSERT INTO users (first_name, last_name, email, password_hash, role)
        VALUES (?, ?, ?, ?, 'admin')
    """, ("Admin", "User", "admin@arpinowalks.it", generate_password_hash("admin12345")))

    cur.execute("""
        INSERT INTO users (first_name, last_name, email, password_hash, role)
        VALUES (?, ?, ?, ?, 'guide')
    """, ("Luca", "Bianchi", "guide@arpinowalks.it", generate_password_hash("guide12345")))
    guide_id = cur.lastrowid

    cur.execute("""
        INSERT INTO users (first_name, last_name, email, password_hash, role)
        VALUES (?, ?, ?, ?, 'participant')
    """, ("Sara", "Rossi", "participant@arpinowalks.it", generate_password_hash("participant12345")))

    # Guide languages
    for lang in ["Italian", "English"]:
        cur.execute("""
            INSERT INTO guide_languages (guide_id, language) VALUES (?, ?)
        """, (guide_id, lang))

    # Tour 1
    cur.execute("""
        INSERT INTO tours (guide_id, title, meeting_point, duration_minutes, language, max_participants, description, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (guide_id, "Medieval Arpino Walk", "Piazza Municipio, Arpino",
          120, "Italian", 10,
          "Discover the ancient walls and towers of Arpino, birthplace of Cicero.", now))
    tour1_id = cur.lastrowid

    for weekday, time in [(5, "10:00"), (6, "10:00")]:
        cur.execute("""
            INSERT INTO tour_schedules (tour_id, weekday, start_time) VALUES (?, ?, ?)
        """, (tour1_id, weekday, time))

    for i, stop in enumerate(["Piazza Municipio", "Acropoli di Arpino", "Torre di Cicerone", "Porta Sanguinara", "Museo Civico"], start=1):
        cur.execute("""
            INSERT INTO tour_stops (tour_id, stop_order, stop_name) VALUES (?, ?, ?)
        """, (tour1_id, i, stop))

    # Tour 2
    cur.execute("""
        INSERT INTO tours (guide_id, title, meeting_point, duration_minutes, language, max_participants, description, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (guide_id, "Cicero's Birthplace Trail", "Fontana di Piazza Municipio, Arpino",
          180, "English", 8,
          "Follow the footsteps of the great Roman orator through the historic center.", now))
    tour2_id = cur.lastrowid

    for weekday, time in [(6, "15:00")]:
        cur.execute("""
            INSERT INTO tour_schedules (tour_id, weekday, start_time) VALUES (?, ?, ?)
        """, (tour2_id, weekday, time))

    for i, stop in enumerate(["Fontana di Piazza Municipio", "Casa di Cicerone", "Mura Ciclopiche", "Arco Romano", "Belvedere del Colle"], start=1):
        cur.execute("""
            INSERT INTO tour_stops (tour_id, stop_order, stop_name) VALUES (?, ?, ?)
        """, (tour2_id, i, stop))

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