from flask import Blueprint, request, jsonify, session, current_app, url_for
from services.paystack import init_transaction, verify_transaction
from models.booking_model import set_booking_reference, record_payment, update_booking_status, get_booking_by_id
from services.qr import generate_qr_for_booking
import os
import secrets

payments_bp = Blueprint("payments_bp", __name__)

def require_auth():
    uid = session.get("user_id")
    role = session.get("role")
    return uid, role

@payments_bp.post("/initialize")
def initialize():
    uid, role = require_auth()
    if not uid or role != "client":
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(force=True)
    booking_id = int(data.get("booking_id"))
    amount = int(data.get("amount"))
    b = get_booking_by_id(current_app.config["DB_PATH"], booking_id)
    if not b or b["client_id"] != uid:
        return jsonify({"error": "not_found"}), 404
    meta = {"booking_id": booking_id, "callback_url": url_for("serve_pages", filename="payment_success.html", _external=True)}
    r = init_transaction(amount, request.headers.get("X-User-Email", "client@example.com"), meta)
    set_booking_reference(current_app.config["DB_PATH"], booking_id, r["reference"])
    return jsonify({"authorization_url": r["authorization_url"], "reference": r["reference"]})

@payments_bp.get("/verify")
def verify():
    uid, role = require_auth()
    if not uid:
        return jsonify({"error": "unauthorized"}), 401
    reference = request.args.get("reference", "")
    b = None
    if reference:
        pass
    r = verify_transaction(reference)
    if r["status"] != "success":
        return jsonify({"error": "payment_failed"}), 400
    conn_b = None
    c = current_app.config["DB_PATH"]
    record_payment(c, int(reference.split("-")[-1]) if reference.startswith("TEST-") else 0, r["amount"], "paid", reference)
    update_booking_status(c, int(reference.split("-")[-1]) if reference.startswith("TEST-") else 0, "paid")
    code = f"BOOKING-{int(reference.split('-')[-1])}-" + secrets.token_hex(8)
    fp = generate_qr_for_booking(c, int(reference.split("-")[-1]) if reference.startswith("TEST-") else 0, code)
    rel = os.path.basename(fp)
    url = url_for("serve_qr", filename=rel, _external=True)
    return jsonify({"status": "success", "qr_image_url": url})

@payments_bp.post("/mock_capture")
def mock_capture():
    uid, role = require_auth()
    if not uid or role != "client":
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(force=True)
    booking_id = int(data.get("booking_id"))
    amount = int(data.get("amount", 5000))
    record_payment(current_app.config["DB_PATH"], booking_id, amount, "paid", f"TEST-{booking_id}")
    update_booking_status(current_app.config["DB_PATH"], booking_id, "paid")
    code = f"BOOKING-{booking_id}-" + secrets.token_hex(8)
    fp = generate_qr_for_booking(current_app.config["DB_PATH"], booking_id, code)
    rel = os.path.basename(fp)
    url = url_for("serve_qr", filename=rel, _external=True)
    return jsonify({"status": "success", "qr_image_url": url, "reference": f"TEST-{booking_id}"})
