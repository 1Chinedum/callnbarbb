from datetime import datetime
from models.db import get_db

def create_user(db_path, name, email, password_hash, role, contact):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO users (name,email,password_hash,role,contact,created_at) VALUES (?,?,?,?,?,?)", (name, email, password_hash, role, contact, datetime.utcnow().isoformat()))
    conn.commit()
    uid = c.lastrowid
    conn.close()
    return uid

def get_user_by_email(db_path, email):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    return row

def get_user_by_id(db_path, user_id):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def create_barber_profile(db_path, user_id, services, price, availability):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO barber_profiles (user_id,services,price,availability,rating) VALUES (?,?,?,?,?)", (user_id, services, price, availability, 0))
    conn.commit()
    conn.close()
    return True

def get_barbers(db_path):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("""SELECT u.id as id,u.name as name,u.contact as contact,u.email as email,
                 bp.services as services,bp.price as price,bp.availability as availability,bp.rating as rating
                 FROM users u JOIN barber_profiles bp ON u.id=bp.user_id""")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_barber_profile(db_path, user_id):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM barber_profiles WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row
