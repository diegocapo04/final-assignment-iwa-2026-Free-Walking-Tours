from db.database import get_connection

def get_photos_by_tour(tour_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT photo_order, image_path
        FROM tour_photos
        WHERE tour_id = ?
        ORDER BY photo_order
    """, (tour_id,))
    photos = cur.fetchall()
    cur.close()
    conn.close()
    return photos

def add_photos_bulk(tour_id, image_paths):
    """
    image_paths: list of paths (max 5)
    """
    conn = get_connection()
    cur = conn.cursor()
    for index, path in enumerate(image_paths, start=1):
        cur.execute("""
            INSERT INTO tour_photos (tour_id, photo_order, image_path)
            VALUES (?, ?, ?)
        """, (tour_id, index, path))
    conn.commit()
    cur.close()
    conn.close()