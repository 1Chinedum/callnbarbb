from flask import Blueprint, jsonify, session, current_app
from models.db import get_db

admin_bp = Blueprint("admin_bp", __name__)

def require_admin():
    uid = session.get("user_id")
    role = session.get("role")
    return uid if uid and role == "admin" else None

@admin_bp.get("/users")
def users():
    if not require_admin():
        return jsonify({"error": "unauthorized"}), 401
    conn = get_db(current_app.config["DB_PATH"])
    c = conn.cursor()
    c.execute("SELECT id,name,email,role,contact,created_at FROM users")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({"users": rows})

@admin_bp.get("/bookings")
def bookings():
    if not require_admin():
        return jsonify({"error": "unauthorized"}), 401
    conn = get_db(current_app.config["DB_PATH"])
    c = conn.cursor()
    c.execute("SELECT * FROM bookings ORDER BY created_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({"bookings": rows})
