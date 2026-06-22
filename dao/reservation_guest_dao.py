from db.database import get_connection

def add_guests_bulk(reservation_id, guests):
    conn = get_connection()
    cur = conn.cursor()
    for guest in guests:
        cur.execute("""
            INSERT INTO reservation_guests (reservation_id, first_name, last_name)
            VALUES (?, ?, ?)
        """, (reservation_id, guest["first_name"], guest["last_name"]))
    conn.commit()
    cur.close()
    conn.close()

def get_guests_by_reservation(reservation_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, first_name, last_name
        FROM reservation_guests
        WHERE reservation_id = ?
        ORDER BY id
    """, (reservation_id,))
    guests = cur.fetchall()
    cur.close()
    conn.close()
    return guests