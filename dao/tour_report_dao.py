from db.database import get_connection
from datetime import datetime

def create_report(tour_id, tour_date, actual_attendees, evidence_photo_path):
    conn = get_connection()
    cur = conn.cursor()
    submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO tour_reports (tour_id, tour_date, actual_attendees, evidence_photo_path, submitted_at)
        VALUES (?, ?, ?, ?, ?)
    """, (tour_id, tour_date, int(actual_attendees), evidence_photo_path, submitted_at))
    conn.commit()
    report_id = cur.lastrowid
    cur.close()
    conn.close()
    return report_id

def get_report(tour_id, tour_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tour_id, tour_date, actual_attendees, evidence_photo_path, submitted_at
        FROM tour_reports
        WHERE tour_id = ? AND tour_date = ?
    """, (tour_id, tour_date))
    report = cur.fetchone()
    cur.close()
    conn.close()
    return report

def get_reports_by_tour(tour_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, tour_id, tour_date, actual_attendees, evidence_photo_path, submitted_at
        FROM tour_reports
        WHERE tour_id = ?
        ORDER BY tour_date
    """, (tour_id,))
    reports = cur.fetchall()
    cur.close()
    conn.close()
    return reports
