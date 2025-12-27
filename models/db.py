import os
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

def get_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password_hash TEXT,
        role TEXT,
        contact TEXT,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS barber_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        services TEXT,
        price INTEGER,
        availability TEXT,
        rating REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        barber_id INTEGER,
        location TEXT,
        date_time TEXT,
        status TEXT,
        paystack_reference TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(client_id) REFERENCES users(id),
        FOREIGN KEY(barber_id) REFERENCES users(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER,
        amount INTEGER,
        status TEXT,
        reference TEXT,
        created_at TEXT,
        FOREIGN KEY(booking_id) REFERENCES bookings(id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS qr_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INTEGER UNIQUE,
        code TEXT,
        image_path TEXT,
        used INTEGER DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY(booking_id) REFERENCES bookings(id)
    )""")
    conn.commit()
    seed_barbers(conn)
    conn.close()

def seed_barbers(conn):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as n FROM users WHERE role='barber'")
    row = c.fetchone()
    if row["n"] == 0:
        now = datetime.utcnow().isoformat()
        b1 = ("Alex Trim", "barber1@example.com", generate_password_hash("password"), "barber", "0800000001", now)
        b2 = ("Bella Fade", "barber2@example.com", generate_password_hash("password"), "barber", "0800000002", now)
        c.execute("INSERT INTO users (name,email,password_hash,role,contact,created_at) VALUES (?,?,?,?,?,?)", b1)
        u1 = c.lastrowid
        c.execute("INSERT INTO users (name,email,password_hash,role,contact,created_at) VALUES (?,?,?,?,?,?)", b2)
        u2 = c.lastrowid
        c.execute("INSERT INTO barber_profiles (user_id,services,price,availability,rating) VALUES (?,?,?,?,?)", (u1, "Haircut, Beard trim", 5000, "Mon-Fri 09:00-17:00", 4.7))
        c.execute("INSERT INTO barber_profiles (user_id,services,price,availability,rating) VALUES (?,?,?,?,?)", (u2, "Fade, Line-up", 6500, "Tue-Sat 10:00-18:00", 4.5))
        conn.commit()
