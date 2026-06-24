from db.database import get_connection

def get_user_count_by_role(role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM users WHERE role = ?", (role,))
    total = cur.fetchone()["total"]
    cur.close()
    conn.close()
    return total

def get_tour_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM tours")
    total = cur.fetchone()["total"]
    cur.close()
    conn.close()
    return total

def get_reservation_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM reservations")
    total = cur.fetchone()["total"]
    cur.close()
    conn.close()
    return total

def get_reservations_count_by_language():
    """Total number of reservations grouped by the language of the booked tour."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.language, COUNT(r.id) AS total
        FROM reservations r
        JOIN tours t ON r.tour_id = t.id
        GROUP BY t.language
        ORDER BY total DESC, t.language
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_all_guides():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, first_name, last_name, email
        FROM users
        WHERE role = 'guide'
        ORDER BY last_name, first_name
    """)
    guides = cur.fetchall()
    cur.close()
    conn.close()
    return guides
