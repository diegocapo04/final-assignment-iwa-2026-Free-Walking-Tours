from db.database import get_connection

def get_stops_by_tour(tour_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT stop_order, stop_name
        FROM tour_stops
        WHERE tour_id = ?
        ORDER BY stop_order
    """, (tour_id,))
    stops = cur.fetchall()
    cur.close()
    conn.close()
    return stops

def add_stops_bulk(tour_id, stop_names):
    """
    stop_names: list of strings with the names of the stops
    """
    conn = get_connection()
    cur = conn.cursor()
    for index, name in enumerate(stop_names, start=1):
        cur.execute("""
            INSERT INTO tour_stops (tour_id, stop_order, stop_name)
            VALUES (?, ?, ?)
        """, (tour_id, index, name))
    conn.commit()
    cur.close()
    conn.close()