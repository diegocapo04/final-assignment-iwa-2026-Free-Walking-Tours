from db.database import get_connection


def get_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM users
        WHERE email = ?
    """, (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM users
        WHERE id = ?
    """, (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


def email_exists(email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id
        FROM users
        WHERE email = ?
    """, (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user is not None


def create_participant(first_name, last_name, email, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (first_name, last_name, email, password_hash, role)
        VALUES (?, ?, ?, ?, 'participant')
    """, (first_name, last_name, email, password_hash))
    conn.commit()
    user_id = cur.lastrowid
    cur.close()
    conn.close()
    return user_id


def create_guide(first_name, last_name, email, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (first_name, last_name, email, password_hash, role)
        VALUES (?, ?, ?, ?, 'guide')
    """, (first_name, last_name, email, password_hash))
    conn.commit()
    user_id = cur.lastrowid
    cur.close()
    conn.close()
    return user_id


def add_guide_language(guide_id, language):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO guide_languages (guide_id, language)
        VALUES (?, ?)
    """, (guide_id, language))
    conn.commit()
    cur.close()
    conn.close()


def add_guide_languages(guide_id, languages):
    conn = get_connection()
    cur = conn.cursor()
    for language in languages:
        cur.execute("""
            INSERT INTO guide_languages (guide_id, language)
            VALUES (?, ?)
        """, (guide_id, language))
    conn.commit()
    cur.close()
    conn.close()


def get_guide_languages(guide_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT language
        FROM guide_languages
        WHERE guide_id = ?
        ORDER BY language
    """, (guide_id,))
    languages = cur.fetchall()
    cur.close()
    conn.close()
    return languages