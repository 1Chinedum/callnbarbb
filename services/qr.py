import os
from datetime import datetime
import qrcode
from models.db import get_db

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def generate_qr_for_booking(db_path, booking_id, code):
    root = os.path.dirname(os.path.abspath(__file__))
    base = os.path.join(os.path.dirname(root), "static", "qr")
    ensure_dir(base)
    img = qrcode.make(code)
    fp = os.path.join(base, f"booking_{booking_id}.png")
    img.save(fp)
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO qr_codes (booking_id,code,image_path,used,created_at) VALUES (?,?,?,?,?)",
              (booking_id, code, fp, 0, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return fp

def verify_qr(db_path, booking_id, code):
    conn = get_db(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM qr_codes WHERE booking_id=?", (booking_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False
    if row["used"] == 1:
        conn.close()
        return False
    if row["code"] != code:
        conn.close()
        return False
    c.execute("UPDATE qr_codes SET used=1 WHERE booking_id=?", (booking_id,))
    conn.commit()
    conn.close()
    return True
