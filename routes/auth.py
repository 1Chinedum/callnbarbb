from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models.user_model import create_user, get_user_by_email, create_barber_profile, get_user_by_id, get_barber_profile

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.post("/signup")
def signup():
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "client")
    contact = data.get("contact", "")
    if not name or not email or not password or role not in ["client", "barber"]:
        return jsonify({"error": "invalid_input"}), 400
    existing = get_user_by_email(current_app.config["DB_PATH"], email)
    if existing:
        return jsonify({"error": "email_exists"}), 409
    uid = create_user(current_app.config["DB_PATH"], name, email, generate_password_hash(password), role, contact)
    if role == "barber":
        price = data.get("price", 5000)
        services = data.get("services", "Haircut")
        availability = data.get("availability", "Mon-Fri 09:00-17:00")
        create_barber_profile(current_app.config["DB_PATH"], uid, services, price, availability)
    session["user_id"] = uid
    session["role"] = role
    return jsonify({"id": uid, "name": name, "email": email, "role": role})

@auth_bp.post("/login")
def login():
    data = request.get_json(force=True)
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    u = get_user_by_email(current_app.config["DB_PATH"], email)
    if not u:
        return jsonify({"error": "invalid_credentials"}), 401
    if not check_password_hash(u["password_hash"], password):
        return jsonify({"error": "invalid_credentials"}), 401
    session["user_id"] = u["id"]
    session["role"] = u["role"]
    profile = None
    if u["role"] == "barber":
        p = get_barber_profile(current_app.config["DB_PATH"], u["id"])
        if p:
            profile = {"services": p["services"], "price": p["price"], "availability": p["availability"], "rating": p["rating"]}
    return jsonify({"id": u["id"], "name": u["name"], "email": u["email"], "role": u["role"], "profile": profile})

@auth_bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"status": "ok"})

@auth_bp.get("/me")
def me():
    uid = session.get("user_id")
    if not uid:
        return jsonify({"authenticated": False}), 200
    u = get_user_by_id(current_app.config["DB_PATH"], uid)
    return jsonify({"authenticated": True, "id": u["id"], "name": u["name"], "email": u["email"], "role": u["role"]})
