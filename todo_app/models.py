from .extensions import db
from datetime import datetime, timezone
from typing import Optional


class Todo(db.Model):
    """
    Model untuk entitas Todo.
    """

    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(255), nullable=False, unique=True)  # judul tugas
    status = db.Column(db.Boolean, default=False, nullable=False)  # selesai/belum
    prioritas = db.Column(
        db.String(10), default="Medium", nullable=False
    )  # High/Medium/Low
    deadline = db.Column(db.Date, nullable=True)  # deadline

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        """
        Representasi string untuk debugging.
        """
        return f"<Todo {self.judul}>"
