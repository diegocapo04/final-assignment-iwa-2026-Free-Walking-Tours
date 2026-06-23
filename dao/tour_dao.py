from db.database import get_connection
from datetime import datetime

def get_tours(language=None, duration_min=None, duration_max=None, weekday=None):
    """
    Returns the public list of tours, optionally filtered by:
    - language (exact match);
    - duration_min / duration_max (minutes);
    - weekday (0=Monday..6=Sunday): only tours that run on that weekday.
    Filters are combined with AND and always use placeholders.
    """
    conditions = []
    params = []

    if language:
        conditions.append("t.language = ?")
        params.append(language)

    if duration_min is not None:
        conditions.append("t.duration_minutes >= ?")
        params.append(duration_min)

    if duration_max is not None:
        conditions.append("t.duration_minutes <= ?")
        params.append(duration_max)

    if weekday is not None:
        conditions.append("""
            EXISTS (
                SELECT 1 FROM tour_schedules ts
                WHERE ts.tour_id = t.id AND ts.weekday = ?
            )
        """)
        params.append(weekday)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
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
        FROM tours t
        JOIN users u ON t.guide_id = u.id
        {where_clause}
        ORDER BY t.title
    """, params)
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
        FROM tours t
        JOIN users u ON t.guide_id = u.id
        WHERE t.id = ?
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

def update_tour_full(tour_id, title, meeting_point, duration_minutes, language, max_participants, description):
    """Used when the tour has no reservations yet: every field can change."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE tours
        SET title = ?,
            meeting_point = ?,
            duration_minutes = ?,
            language = ?,
            max_participants = ?,
            description = ?
        WHERE id = ?
    """, (title, meeting_point, int(duration_minutes), language, int(max_participants), description, tour_id))
    conn.commit()
    cur.close()
    conn.close()

def update_tour_text(tour_id, title, description):
    """Used when the tour is locked: only title and description can change."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE tours
        SET title = ?,
            description = ?
        WHERE id = ?
    """, (title, description, tour_id))
    conn.commit()
    cur.close()
    conn.close()

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