from datetime import datetime
from models.db import get_db

def create_booking(db_path, client_id, barber_id, location, date_time):
    conn = get_db(db_path)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute("INSERT INTO bookings (client_id,barber_id,location,date_time,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",
              (client_id, barber_id, location, date_time, "pending_payment", now, now))
    conn.commit()
    bid = c.lastrowid
    conn.close()
    return bid

def get_booking_by_id(db_path, booking_id):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM bookings WHERE id=?", (booking_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_bookings_for_client(db_path, client_id):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("""SELECT b.*, u.name as barber_name FROM bookings b
                 JOIN users u ON b.barber_id=u.id WHERE b.client_id=?
                 ORDER BY b.created_at DESC""", (client_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_bookings_for_barber(db_path, barber_id):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("""SELECT b.*, u.name as client_name FROM bookings b
                 JOIN users u ON b.client_id=u.id WHERE b.barber_id=?
                 ORDER BY b.created_at DESC""", (barber_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_booking_status(db_path, booking_id, status):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("UPDATE bookings SET status=?, updated_at=? WHERE id=?", (status, datetime.utcnow().isoformat(), booking_id))
    conn.commit()
    conn.close()
    return True

def set_booking_reference(db_path, booking_id, reference):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("UPDATE bookings SET paystack_reference=?, updated_at=? WHERE id=?", (reference, datetime.utcnow().isoformat(), booking_id))
    conn.commit()
    conn.close()
    return True

def record_payment(db_path, booking_id, amount, status, reference):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO payments (booking_id,amount,status,reference,created_at) VALUES (?,?,?,?,?)",
              (booking_id, amount, status, reference, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return True

def compute_earnings_for_barber(db_path, barber_id):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("""SELECT COALESCE(SUM(amount),0) as total FROM payments p
                 JOIN bookings b ON p.booking_id=b.id
                 WHERE b.barber_id=? AND p.status='paid'""", (barber_id,))
    row = c.fetchone()
    conn.close()
    return row["total"] if row else 0
