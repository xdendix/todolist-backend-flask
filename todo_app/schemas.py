from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validates, ValidationError, post_dump
from .models import Todo
from .constants import PRIORITIES, ERROR_MESSAGES
import datetime
from typing import Any, Dict


class TodoSchema(SQLAlchemyAutoSchema):
    """
    Schema for serialization and validation of Todo.
    Fields are ordered with id first and timestamps last.
    """

    class Meta:
        model = Todo
        load_instance = True
        sqla_session = None
        ordered = True
        fields = ('id', 'judul', 'status', 'prioritas', 'deadline', 'created_at', 'updated_at')

    # Desired field order: id, judul, status, prioritas, deadline, created_at, updated_at
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
        Validate priority value.
        """
        if value and value.capitalize() not in PRIORITIES:
            raise ValidationError(ERROR_MESSAGES["invalid_priority"])

    @validates("deadline")
    def validate_deadline(self, value: Any, **kwargs) -> None:
        """
        Validate deadline format.
        """
        if value and not isinstance(value, datetime.date):
            raise ValidationError(ERROR_MESSAGES["invalid_deadline"])

    @validates("judul")
    def validate_judul(self, value: str, **kwargs) -> None:
        """
        Validate title is not empty.
        """
        if not value or not value.strip():
            raise ValidationError(ERROR_MESSAGES["empty_title"])

    @post_dump
    def order_fields(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Order fields in response with id first and timestamps last.
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
