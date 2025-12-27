import os
from flask import Flask, jsonify, request, session, send_from_directory, send_file
from models.db import init_db
from routes.auth import auth_bp
from routes.bookings import bookings_bp
from routes.payments import payments_bp
from routes.admin import admin_bp

def create_app():
    app = Flask(__name__, static_folder=None)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-key")
    app.config["DB_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "app.db")
    init_db(app.config["DB_PATH"])

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(bookings_bp, url_prefix="/api")
    app.register_blueprint(payments_bp, url_prefix="/api/payments")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.get("/")
    def serve_index():
        root = os.path.dirname(os.path.abspath(__file__))
        return send_file(os.path.join(root, "index.html"))

    @app.get("/pages/<path:filename>")
    def serve_pages(filename):
        root = os.path.dirname(os.path.abspath(__file__))
        return send_file(os.path.join(root, "pages", filename))

    @app.get("/css/<path:filename>")
    def serve_css(filename):
        root = os.path.dirname(os.path.abspath(__file__))
        return send_from_directory(os.path.join(root, "css"), filename)

    @app.get("/js/<path:filename>")
    def serve_js(filename):
        root = os.path.dirname(os.path.abspath(__file__))
        return send_from_directory(os.path.join(root, "js"), filename)

    @app.get("/assets/<path:filename>")
    def serve_assets(filename):
        root = os.path.dirname(os.path.abspath(__file__))
        return send_from_directory(os.path.join(root, "assets"), filename)

    @app.get("/static/qr/<path:filename>")
    def serve_qr(filename):
        root = os.path.dirname(os.path.abspath(__file__))
        return send_from_directory(os.path.join(root, "static", "qr"), filename)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
