from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError, post_dump
from .models import Todo
import datetime
from typing import Any


class TodoSchema(SQLAlchemyAutoSchema):
    """
    Schema untuk serialisasi dan validasi Todo.
    Field diurutkan dengan id di atas dan timestamps di bawah.
    """

    class Meta:
        model = Todo
        load_instance = True
        sqla_session = None
        ordered = True
        fields = ('id', 'judul', 'status', 'prioritas', 'deadline', 'created_at', 'updated_at')

    # Urutan field yang diinginkan: id, judul, status, prioritas, deadline, created_at, updated_at
    id = fields.Int(dump_only=True)
    judul = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    status = fields.Bool()
    prioritas = fields.Str(required=False)
    deadline = fields.Date(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates("prioritas")
    def validate_prioritas(self, value: str, **kwargs) -> None:
        """
        Validasi nilai prioritas.
        """
        if value and value.capitalize() not in ["High", "Medium", "Low"]:
            raise ValidationError("Prioritas hanya boleh High, Medium, atau Low.")

    @validates("deadline")
    def validate_deadline(self, value: Any, **kwargs) -> None:
        """
        Validasi format deadline.
        """
        if value and not isinstance(value, datetime.date):
            raise ValidationError("Format deadline tidak valid (gunakan YYYY-MM-DD).")

    @validates("judul")
    def validate_judul(self, value: str, **kwargs) -> None:
        """
        Validasi judul tidak kosong.
        """
        if not value or not value.strip():
            raise ValidationError("Judul tidak boleh kosong.")

    @post_dump
    def order_fields(self, data: dict, **kwargs) -> dict:
        """
        Mengurutkan field dalam response dengan id di atas dan timestamps di bawah.
        """
        return {
            "id": data.get("id"),
            "judul": data.get("judul"),
            "status": data.get("status"),
            "prioritas": data.get("prioritas"),
            "deadline": data.get("deadline"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }
