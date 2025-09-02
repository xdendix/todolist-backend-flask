import os
from dotenv import load_dotenv
from todo_app import create_app
from typing import Optional

# Memuat variabel environment dari instance/.env jika ada
load_dotenv(os.path.join("instance", ".env"))

# Membuat aplikasi menggunakan factory pattern
app = create_app()

def get_port() -> int:
    """
    Mendapatkan port dari environment variable PORT.
    Jika tidak ada, gunakan default 5000.
    """
    port_str: Optional[str] = os.environ.get("PORT")
    if port_str and port_str.isdigit():
        return int(port_str)
    return 5000

if __name__ == "__main__":
    # Menjalankan server development Flask
    app.run(
        host="0.0.0.0",
        port=get_port(),
        debug=app.config.get("DEBUG", True),
    )
