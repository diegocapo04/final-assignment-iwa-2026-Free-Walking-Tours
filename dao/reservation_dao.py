from db.database import get_connection
from datetime import datetime

def create_reservation(participant_id, tour_id, tour_date, total_people):
    conn = get_connection()
    cur = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO reservations (participant_id, tour_id, tour_date, total_people, status, created_at, cancelled_at)
        VALUES (?, ?, ?, ?, 'active', ?, NULL)
    """, (participant_id, tour_id, tour_date, total_people, created_at))
    conn.commit()
    reservation_id = cur.lastrowid
    cur.close()
    conn.close()
    return reservation_id

def get_reservation_by_id(reservation_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            r.id,
            r.participant_id,
            r.tour_id,
            r.tour_date,
            r.total_people,
            r.status,
            r.created_at,
            r.cancelled_at
        FROM reservations r
        WHERE r.id = ?
    """, (reservation_id,))
    reservation = cur.fetchone()
    cur.close()
    conn.close()
    return reservation

def get_active_reservations_for_tour_date(tour_id, tour_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            id,
            participant_id,
            tour_id,
            tour_date,
            total_people,
            status,
            created_at,
            cancelled_at
        FROM reservations
        WHERE tour_id = ?
          AND tour_date = ?
          AND status = 'active'
        ORDER BY created_at
    """, (tour_id, tour_date))
    reservations = cur.fetchall()
    cur.close()
    conn.close()
    return reservations

def get_reserved_places_for_tour_date(tour_id, tour_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COALESCE(SUM(total_people), 0) AS reserved_places
        FROM reservations
        WHERE tour_id = ?
          AND tour_date = ?
          AND status = 'active'
    """, (tour_id, tour_date))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row["reserved_places"]

def get_active_reservations_by_participant(participant_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            r.id,
            r.participant_id,
            r.tour_id,
            r.tour_date,
            r.total_people,
            r.status,
            r.created_at,
            r.cancelled_at,
            t.title,
            t.meeting_point,
            t.duration_minutes,
            t.language,
            ts.start_time
        FROM reservations r
        JOIN tours t ON r.tour_id = t.id
        JOIN tour_schedules ts ON ts.tour_id = t.id
          AND ts.weekday = ((CAST(strftime('%w', r.tour_date) AS INTEGER) + 6) % 7)
        WHERE r.participant_id = ?
          AND r.status = 'active'
        ORDER BY r.tour_date, ts.start_time
    """, (participant_id,))
    reservations = cur.fetchall()
    cur.close()
    conn.close()
    return reservations

def get_all_reservations_by_participant(participant_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            r.id,
            r.participant_id,
            r.tour_id,
            r.tour_date,
            r.total_people,
            r.status,
            r.created_at,
            r.cancelled_at,
            t.title,
            t.meeting_point,
            t.duration_minutes,
            t.language,
            ts.start_time
        FROM reservations r
        JOIN tours t ON r.tour_id = t.id
        JOIN tour_schedules ts ON ts.tour_id = t.id
          AND ts.weekday = ((CAST(strftime('%w', r.tour_date) AS INTEGER) + 6) % 7)
        WHERE r.participant_id = ?
        ORDER BY r.tour_date DESC, ts.start_time DESC
    """, (participant_id,))
    reservations = cur.fetchall()
    cur.close()
    conn.close()
    return reservations

def cancel_reservation(reservation_id):
    conn = get_connection()
    cur = conn.cursor()
    cancelled_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        UPDATE reservations
        SET status = 'cancelled',
            cancelled_at = ?
        WHERE id = ?
    """, (cancelled_at, reservation_id))
    conn.commit()
    cur.close()
    conn.close()

def tour_has_active_reservations(tour_id):
    """
    Used to lock the essential fields of a tour once someone has reserved.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1
        FROM reservations
        WHERE tour_id = ?
          AND status = 'active'
        LIMIT 1
    """, (tour_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row is not None

def get_active_reservations_with_participant(tour_id):
    """
    Active reservations of a tour with the booking participant's name and the
    start time of the chosen date. Used by the guide profile and reporting.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            r.id,
            r.tour_date,
            r.total_people,
            ts.start_time,
            u.first_name,
            u.last_name
        FROM reservations r
        JOIN users u ON r.participant_id = u.id
        JOIN tours t ON r.tour_id = t.id
        JOIN tour_schedules ts ON ts.tour_id = t.id
          AND ts.weekday = ((CAST(strftime('%w', r.tour_date) AS INTEGER) + 6) % 7)
        WHERE r.tour_id = ?
          AND r.status = 'active'
        ORDER BY r.tour_date, ts.start_time, u.last_name
    """, (tour_id,))
    reservations = cur.fetchall()
    cur.close()
    conn.close()
    return reservations

def get_reservation_detail_for_participant(reservation_id, participant_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            r.id,
            r.participant_id,
            r.tour_id,
            r.tour_date,
            r.total_people,
            r.status,
            r.created_at,
            r.cancelled_at,
            t.title,
            t.meeting_point,
            t.duration_minutes,
            t.language,
            ts.start_time
        FROM reservations r
        JOIN tours t ON r.tour_id = t.id
        JOIN tour_schedules ts ON ts.tour_id = t.id
          AND ts.weekday = ((CAST(strftime('%w', r.tour_date) AS INTEGER) + 6) % 7)
        WHERE r.id = ?
          AND r.participant_id = ?
    """, (reservation_id, participant_id))
    reservation = cur.fetchone()
    cur.close()
    conn.close()
    return reservation