from db.database import get_connection
from datetime import datetime

def get_tours():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            t.id,
            t.title,
            t.meeting_point,
            t.duration_minutes,
            t.language,
            t.max_participants,
            t.description,
            t.created_at,
            u.first_name || ' ' || u.last_name AS guide_name
        FROM tours t, users u
        WHERE t.guide_id = u.id
        ORDER BY t.title
    """)
    tours = cur.fetchall()
    cur.close()
    conn.close()
    return tours

def get_tour_by_id(tour_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            t.id,
            t.guide_id,
            t.title,
            t.meeting_point,
            t.duration_minutes,
            t.language,
            t.max_participants,
            t.description,
            t.created_at,
            u.first_name || ' ' || u.last_name AS guide_name
        FROM tours t, users u
        WHERE t.guide_id = u.id AND t.id = ?
    """, (tour_id,))
    tour = cur.fetchone()
    cur.close()
    conn.close()
    return tour

def get_tours_by_guide(guide_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            id,
            title,
            meeting_point,
            duration_minutes,
            language,
            max_participants,
            description,
            created_at
        FROM tours
        WHERE guide_id = ?
        ORDER BY title
    """, (guide_id,))
    tours = cur.fetchall()
    cur.close()
    conn.close()
    return tours

def create_tour(guide_id, title, meeting_point, duration_minutes, language, max_participants, description):
    conn = get_connection()
    cur = conn.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO tours (guide_id, title, meeting_point, duration_minutes, language, max_participants, description, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (guide_id, title, meeting_point, int(duration_minutes), language, int(max_participants), description, created_at))
    conn.commit()
    tour_id = cur.lastrowid
    cur.close()
    conn.close()
    return tour_id

def delete_tour(tour_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM tours
        WHERE id = ?
    """, (tour_id,))
    conn.commit()
    cur.close()
    conn.close()