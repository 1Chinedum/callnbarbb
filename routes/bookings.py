from flask import Blueprint, request, jsonify, session, current_app, url_for
from models.user_model import get_barbers, get_user_by_id
from models.booking_model import create_booking, get_bookings_for_client, get_bookings_for_barber, update_booking_status, get_booking_by_id, compute_earnings_for_barber
from services.qr import generate_qr_for_booking, verify_qr
import os
import secrets

bookings_bp = Blueprint("bookings_bp", __name__)

def require_auth():
    uid = session.get("user_id")
    role = session.get("role")
    return uid, role

@bookings_bp.get("/barbers")
def list_barbers():
    data = get_barbers(current_app.config["DB_PATH"])
    return jsonify({"barbers": data})

@bookings_bp.get("/bookings")
def list_bookings():
    uid, role = require_auth()
    if not uid:
        return jsonify({"error": "unauthorized"}), 401
    if role == "client":
        rows = get_bookings_for_client(current_app.config["DB_PATH"], uid)
        return jsonify({"bookings": rows})
    if role == "barber":
        rows = get_bookings_for_barber(current_app.config["DB_PATH"], uid)
        return jsonify({"bookings": rows})
    return jsonify({"bookings": []})

@bookings_bp.post("/bookings")
def create_booking_route():
    uid, role = require_auth()
    if not uid or role != "client":
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(force=True)
    barber_id = int(data.get("barber_id"))
    location = data.get("location", "")
    date_time = data.get("date_time", "")
    if not barber_id or not location or not date_time:
        return jsonify({"error": "invalid_input"}), 400
    bid = create_booking(current_app.config["DB_PATH"], uid, barber_id, location, date_time)
    return jsonify({"booking_id": bid, "status": "pending_payment"})

@bookings_bp.post("/bookings/<int:booking_id>/accept")
def accept_booking(booking_id):
    uid, role = require_auth()
    if not uid or role != "barber":
        return jsonify({"error": "unauthorized"}), 401
    b = get_booking_by_id(current_app.config["DB_PATH"], booking_id)
    if not b or b["barber_id"] != uid:
        return jsonify({"error": "not_found"}), 404
    update_booking_status(current_app.config["DB_PATH"], booking_id, "accepted")
    return jsonify({"status": "accepted"})

@bookings_bp.post("/bookings/<int:booking_id>/decline")
def decline_booking(booking_id):
    uid, role = require_auth()
    if not uid or role != "barber":
        return jsonify({"error": "unauthorized"}), 401
    b = get_booking_by_id(current_app.config["DB_PATH"], booking_id)
    if not b or b["barber_id"] != uid:
        return jsonify({"error": "not_found"}), 404
    update_booking_status(current_app.config["DB_PATH"], booking_id, "declined")
    return jsonify({"status": "declined"})

@bookings_bp.get("/bookings/<int:booking_id>/qr")
def get_qr(booking_id):
    uid, role = require_auth()
    if not uid:
        return jsonify({"error": "unauthorized"}), 401
    b = get_booking_by_id(current_app.config["DB_PATH"], booking_id)
    if not b or (uid != b["client_id"] and uid != b["barber_id"]):
        return jsonify({"error": "not_found"}), 404
    code = f"BOOKING-{booking_id}-{secrets.token_hex(8)}"
    fp = generate_qr_for_booking(current_app.config["DB_PATH"], booking_id, code)
    rel = os.path.basename(fp)
    url = url_for("serve_qr", filename=rel, _external=True)
    return jsonify({"image_url": url})

@bookings_bp.post("/bookings/<int:booking_id>/verify_qr")
def verify_qr_route(booking_id):
    uid, role = require_auth()
    if not uid or role != "barber":
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(force=True)
    code = data.get("code", "")
    b = get_booking_by_id(current_app.config["DB_PATH"], booking_id)
    if not b or b["barber_id"] != uid:
        return jsonify({"error": "not_found"}), 404
    ok = verify_qr(current_app.config["DB_PATH"], booking_id, code)
    if not ok:
        return jsonify({"error": "invalid_qr"}), 400
    update_booking_status(current_app.config["DB_PATH"], booking_id, "completed")
    return jsonify({"status": "completed"})

@bookings_bp.get("/barber/earnings")
def barber_earnings():
    uid, role = require_auth()
    if not uid or role != "barber":
        return jsonify({"error": "unauthorized"}), 401
    total = compute_earnings_for_barber(current_app.config["DB_PATH"], uid)
    return jsonify({"total": int(total)})
