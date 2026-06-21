from db.database import get_connection

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def get_schedules_by_tour(tour_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT weekday, start_time
        FROM tour_schedules
        WHERE tour_id = ?
        ORDER BY weekday
    """, (tour_id,))
    schedules = cur.fetchall()
    cur.close()
    conn.close()
    return schedules

def add_schedules_bulk(tour_id, schedules):
    """
    schedules: list of dictionaries with keys 'weekday' (int 0-6) and 'start_time' (str HH:MM)
    """
    conn = get_connection()
    cur = conn.cursor()
    for s in schedules:
        cur.execute("""
            INSERT INTO tour_schedules (tour_id, weekday, start_time)
            VALUES (?, ?, ?)
        """, (tour_id, s["weekday"], s["start_time"]))
    conn.commit()
    cur.close()
    conn.close()