# TodoList Backend Flask

A RESTful API for Todo List management built with Flask, SQLAlchemy, and Marshmallow.

## Features

- ✅ **CRUD Operations**: Create, Read, Update, Delete todos
- 🔍 **Search & Filter**: Search by keyword, priority, status, and deadline
- ✅ **Data Validation**: Comprehensive input validation with Marshmallow
- 🏗️ **Factory Pattern**: Clean application structure with Flask factory pattern
- 📝 **API Documentation**: Complete Postman collection for testing
- 🔒 **Environment Configuration**: Secure environment variable management

## Tech Stack

- **Framework**: Flask 3.0+
- **Database**: SQLAlchemy with SQLite
- **Serialization**: Marshmallow & Marshmallow-SQLAlchemy
- **CORS**: Flask-CORS for cross-origin requests
- **Environment**: python-dotenv for configuration

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd todolist-backend-flask
   ```

2. **Create virtual environment**
   ```bash
   python -m venv todolist_backend_venv
   source todolist_backend_venv/bin/activate  # On Windows: todolist_backend_venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at: `http://127.0.0.1:5000`

## API Endpoints

### Health Check
- **GET** `/health` - Check API status

### Todo Management
- **GET** `/api/todos/` - Get all todos
- **POST** `/api/todos/` - Create new todo
- **GET** `/api/todos/<id>` - Get todo by ID
- **PUT** `/api/todos/<id>` - Update todo
- **DELETE** `/api/todos/<id>` - Delete todo

### Search & Filter
- **GET** `/api/todos/search` - Search todos with filters
  - Query parameters: `q`, `prioritas`, `status`, `deadline`

## Request/Response Examples

### Create Todo
```bash
POST /api/todos/
Content-Type: application/json

{
  "judul": "Belajar Flask",
  "prioritas": "High",
  "status": false,
  "deadline": "2025-12-31"
}
```

### Search Todos
```bash
GET /api/todos/search?q=flask&prioritas=High
```

## Data Models

### Todo
- `id`: Integer (Primary Key)
- `judul`: String (Required, Unique)
- `status`: Boolean (Default: false)
- `prioritas`: String (High/Medium/Low)
- `deadline`: Date (Optional)
- `created_at`: DateTime (Auto-generated)
- `updated_at`: DateTime (Auto-updated)

## Validation Rules

- **judul**: Cannot be empty or whitespace only
- **prioritas**: Must be "High", "Medium", or "Low" (case insensitive)
- **deadline**: Must be valid date format (YYYY-MM-DD)
- **status**: Boolean value

## Testing with Postman

1. **Import Collection**
   - Import `TodoList_API_Postman_Collection.json` into Postman

2. **Setup Environment**
   - Create environment variable: `base_url` = `http://127.0.0.1:5000`

3. **Start Testing**
   - Run requests in order or as needed

## Project Structure

```
todolist-backend-flask/
├── app.py                      # Application entry point
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
├── TODO.md                    # Development tasks
├── POSTMAN_TESTING_GUIDE.md   # Testing documentation
├── TodoList_API_Postman_Collection.json  # Postman collection
├── Postman_Import_Instructions.md       # Import guide
├── instance/                  # Instance-specific config
├── todo_app/                  # Main application package
│   ├── __init__.py           # Flask app factory
│   ├── extensions.py         # Flask extensions
│   ├── models.py             # Database models
│   ├── schemas.py            # Marshmallow schemas
│   └── todos/                # Todos blueprint
│       └── routes.py         # API routes
└── todolist_backend_venv/    # Virtual environment
```

## Environment Variables

### ⚠️ PENTING: Setup Keamanan

**JANGAN pernah commit file `.env` ke version control!**

1. **Copy file template:**
   ```bash
   cp instance/.env.example instance/.env
   ```

2. **Generate SECRET_KEY yang aman:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Update file `.env` dengan key yang di-generate**

### File Environment Variables

File `.env` di folder `instance/` berisi:

```env
# KEAMANAN - WAJIB diisi dengan key yang aman
SECRET_KEY=be1b4d4345d37fa106b537dc5788acaaaf74f1bd7cde277ff8a6b31ce7cc168a

# DATABASE
DATABASE_URL=sqlite:///data.db

# APLIKASI
FLASK_DEBUG=1
PORT=5000
```

### 🔒 Security Best Practices

- ✅ **SECRET_KEY**: Gunakan key random minimal 32 karakter
- ✅ **Environment Variables**: Jangan hardcode sensitive data
- ✅ **.env file**: Sudah di-ignore oleh .gitignore
- ✅ **Production**: Gunakan key yang berbeda dari development
- ✅ **Version Control**: Jangan commit file .env

## Development

### Code Quality
- Type hints added for better IDE support
- Comprehensive docstrings
- Consistent error handling
- Input validation with Marshmallow

### Database
- SQLite for development (easy setup)
- SQLAlchemy for ORM
- Automatic table creation
- Foreign key relationships support

### API Design
- RESTful endpoints
- JSON request/response
- Proper HTTP status codes
- Detailed error messages

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

This project is open source and available under the [MIT License](LICENSE).

---

**Happy Coding! 🚀**
