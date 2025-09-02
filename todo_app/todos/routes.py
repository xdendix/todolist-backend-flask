from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Todo
from ..schemas import TodoSchema
from marshmallow import ValidationError
from typing import Dict, Any, List

bp = Blueprint("todos", __name__)

todo_schema = TodoSchema(session=db.session)
todos_schema = TodoSchema(many=True, session=db.session)


# Mendapatkan semua todo
@bp.route("/", methods=["GET"])
def list_todos():
    """
    Mendapatkan daftar semua todo, diurutkan berdasarkan waktu pembuatan terbaru.
    Response body diurutkan dengan id di atas dan created_at/updated_at di bawah.
    Mendukung pagination dengan query parameter page dan per_page.
    """
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    # Ensure reasonable limits
    if per_page > 100:
        per_page = 100
    if page < 1:
        page = 1

    pagination = Todo.query.order_by(Todo.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    todos_data = todos_schema.dump(pagination.items)

    return (
        jsonify(
            {
                "success": True,
                "count": len(todos_data),
                "data": todos_data,
                "pagination": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                }
            }
        ),
        200,
    )


# Membuat todo baru
@bp.route("/", methods=["POST"])
def create_todo():
    """
    Membuat todo baru berdasarkan data JSON yang dikirim.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Input tidak diberikan"}), 400
    try:
        todo = todo_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 400

    # Check for duplicate judul
    existing_todo = Todo.query.filter_by(judul=json_data.get("judul")).first()
    if existing_todo:
        return jsonify({"message": "Judul todo sudah ada, gunakan judul lain."}), 400

    db.session.add(todo)
    db.session.commit()
    return jsonify(todo_schema.dump(todo)), 201


# Mendapatkan todo berdasarkan ID
@bp.route("/<int:todo_id>", methods=["GET"])
def get_todo(todo_id: int):
    """
    Mendapatkan todo berdasarkan ID.
    """
    todo = Todo.query.get_or_404(todo_id)
    result = todo_schema.dump(todo)
    return jsonify(result), 200


# Memperbarui todo (PUT/PATCH)
@bp.route("/<int:todo_id>", methods=["PUT", "PATCH"])
def update_todo(todo_id: int):
    """
    Memperbarui todo berdasarkan ID dengan data JSON yang dikirim.
    """
    todo = Todo.query.get_or_404(todo_id)
    json_data = request.get_json() or {}

    # Check if at least one field is provided for update
    if not json_data:
        return jsonify({"message": "Tidak ada data yang diberikan untuk update"}), 400

    try:
        updated = todo_schema.load(json_data, instance=todo, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.commit()
    return jsonify(todo_schema.dump(updated)), 200


# Menghapus todo berdasarkan ID
@bp.route("/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id: int):
    """
    Menghapus todo berdasarkan ID.
    """
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return "", 204


# Filter: pencarian tugas
@bp.route("/search", methods=["GET"])
def search_todo():
    """
    Mencari todo berdasarkan query parameter:
    - q: kata kunci judul (case insensitive)
    - prioritas: High, Medium, Low
    - status: selesai, belum selesai
    - deadline: tanggal deadline (YYYY-MM-DD)
    - deadline_from: tanggal deadline dari (YYYY-MM-DD)
    - deadline_to: tanggal deadline sampai (YYYY-MM-DD)
    """
    kata_kunci = request.args.get("q", "").lower()
    prioritas = request.args.get("prioritas", "").capitalize()
    status = request.args.get("status", "").lower()
    deadline = request.args.get("deadline", "")
    deadline_from = request.args.get("deadline_from", "")
    deadline_to = request.args.get("deadline_to", "")

    query = Todo.query

    if kata_kunci:
        query = query.filter(Todo.judul.ilike(f"%{kata_kunci}%"))

    if prioritas in ["High", "Medium", "Low"]:
        query = query.filter_by(prioritas=prioritas)

    if status == "selesai":
        query = query.filter_by(status=True)
    elif status == "belum selesai":
        query = query.filter_by(status=False)

    if deadline:
        query = query.filter_by(deadline=deadline)

    if deadline_from:
        query = query.filter(Todo.deadline >= deadline_from)

    if deadline_to:
        query = query.filter(Todo.deadline <= deadline_to)

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))

    # Ensure reasonable limits
    if per_page > 100:
        per_page = 100
    if page < 1:
        page = 1

    pagination = query.order_by(Todo.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    results_data = todos_schema.dump(pagination.items)

    return jsonify(
        {
            "success": True,
            "count": len(results_data),
            "data": results_data,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }
        }
    ), 200
