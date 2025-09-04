"""
API Documentation setup using Flask-RESTX
"""
from flask_restx import Api, fields
from .constants import RESPONSE_SUCCESS, RESPONSE_MESSAGE, RESPONSE_DATA, RESPONSE_COUNT, RESPONSE_PAGINATION

# Create API instance
api = Api(
    title="Todo API",
    version="1.0",
    description="A RESTful API for managing todos with full CRUD operations",
    doc="/docs",  # Swagger UI will be available at /docs
    prefix="/api"
)

# Define models for documentation
todo_model = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The todo unique identifier'),
    'judul': fields.String(required=True, description='The todo title', example='Learn Python'),
    'status': fields.Boolean(description='Todo completion status', example=False),
    'prioritas': fields.String(description='Todo priority level', enum=['High', 'Medium', 'Low'], example='High'),
    'deadline': fields.Date(description='Todo deadline (YYYY-MM-DD)', example='2025-12-31'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(readonly=True, description='Last update timestamp')
})

pagination_model = api.model('Pagination', {
    'page': fields.Integer(description='Current page number'),
    'per_page': fields.Integer(description='Items per page'),
    'total': fields.Integer(description='Total number of items'),
    'pages': fields.Integer(description='Total number of pages'),
    'has_next': fields.Boolean(description='Whether there is a next page'),
    'has_prev': fields.Boolean(description='Whether there is a previous page')
})

response_model = api.model('Response', {
    RESPONSE_SUCCESS: fields.Boolean(description='Operation success status'),
    RESPONSE_MESSAGE: fields.String(description='Response message'),
    RESPONSE_DATA: fields.Raw(description='Response data'),
    RESPONSE_COUNT: fields.Integer(description='Number of items in response'),
    RESPONSE_PAGINATION: fields.Nested(pagination_model, description='Pagination information')
})

# Define namespaces
todos_ns = api.namespace('todos', description='Todo operations')

# Add models to namespace
todos_ns.models['Todo'] = todo_model
todos_ns.models['Response'] = response_model
todos_ns.models['Pagination'] = pagination_model
