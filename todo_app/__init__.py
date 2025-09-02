from flask import Flask
from .extensions import db
from .todos.routes import bp as todos_bp
import os
from typing import Optional


def create_app(config_object: Optional[str] = None) -> Flask:
    """
    Factory function untuk membuat instance Flask app.
    Bisa menerima nama config class atau memakai default.
    """

    app = Flask(__name__, instance_relative_config=True)

    # Validasi dan konfigurasi SECRET_KEY (WAJIB untuk keamanan)
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise ValueError(
            "SECRET_KEY tidak ditemukan! "
            "Silakan set environment variable SECRET_KEY atau buat file .env di folder instance/. "
            "Lihat instance/.env.example untuk contoh konfigurasi."
        )

    # Konfigurasi dasar aplikasi
    app.config.from_mapping(
        SECRET_KEY=secret_key,
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///data.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DEBUG=os.environ.get("FLASK_DEBUG", "1") == "1",
    )

    # Inisialisasi ekstensi database
    try:
        db.init_app(app)
    except Exception as e:
        app.logger.error(f"Error saat inisialisasi database: {e}")
        raise

    # Registrasi blueprint todos
    app.register_blueprint(todos_bp, url_prefix="/api/todos")

    # Endpoint health check
    @app.route("/health")
    def health():
        """
        Endpoint untuk pengecekan status aplikasi.
        """
        return {"status": "ok"}

    # Buat tabel otomatis saat pertama kali (hanya untuk development,
    # sebaiknya menggunakan migrasi database di production)
    with app.app_context():
        db.create_all()

    return app
