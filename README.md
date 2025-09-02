# 📋 TodoList Backend Flask

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask 3.0+](https://img.shields.io/badge/flask-3.0+-red.svg)](https://flask.palletsprojects.com/)

A robust RESTful API for Todo List management built with Flask, SQLAlchemy, and Marshmallow. Features comprehensive CRUD operations, advanced search and filtering, secure environment management, and extensive testing coverage.

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
- **Rate Limiting**: Flask-Limiter for API rate limiting
- **Environment**: python-dotenv for configuration
- **Testing**: pytest with Flask-Testing

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/xdendix/todolist-backend-flask.git
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

4. **Configure environment variables securely**

   - Copy the example environment file:
     ```bash
     cp instance/.env.example instance/.env
     ```

   - Generate a secure SECRET_KEY:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```

   - Edit `instance/.env` and replace the SECRET_KEY value with the generated key.

   - **Important Security Notes:**
     - Never commit your `.env` file to version control.
     - The `.env` file is included in `.gitignore` to prevent accidental commits.
     - Keep your SECRET_KEY and other sensitive data private.
     - Use different keys for development and production environments.

5. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at: `http://127.0.0.1:5000`

## API Endpoints

### Health Check
- **GET** `/health` - Check API status

### Todo Management
- **GET** `/api/todos/` - Get all todos (with pagination)
  - Query parameters: `page` (default: 1), `per_page` (default: 10, max: 100)
- **POST** `/api/todos/` - Create new todo
- **GET** `/api/todos/<id>` - Get todo by ID
- **PUT** `/api/todos/<id>` - Update todo
- **DELETE** `/api/todos/<id>` - Delete todo

### Search & Filter
- **GET** `/api/todos/search` - Search todos with filters
  - Query parameters: `q` (keyword), `prioritas`, `status`, `deadline`, `deadline_from`, `deadline_to`, `page`, `per_page`

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
GET /api/todos/search?q=flask&prioritas=High&status=belum%20selesai&deadline_from=2025-01-01&deadline_to=2025-12-31
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

## Running Tests

The project includes comprehensive unit and integration tests using pytest.

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test
```bash
python run_tests.py test_create_todo_success
```

### Run Tests with Coverage
```bash
pytest --cov=todo_app --cov-report=html
```

### Test Structure
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints and database interactions
- **Fixtures**: Pre-configured test data and app instances

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
│   ├── .env.example          # Example environment variables file (do not commit)
│   └── .env                  # Local environment variables file (ignored by git)
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

### 🔒 Security Best Practices

- ✅ **SECRET_KEY**: Gunakan key random minimal 32 karakter
- ✅ **Environment Variables**: Jangan hardcode sensitive data
- ✅ **.env file**: Sudah di-ignore oleh .gitignore
- ✅ **Production**: Gunakan key yang berbeda dari development
- ✅ **Version Control**: Jangan commit file .env
- ✅ **File Permissions**: Set restrictive permissions on .env file (chmod 600)
- ✅ **Regular Rotation**: Rotate SECRET_KEY periodically
- ✅ **Environment Separation**: Use different .env files for dev/staging/production
- ✅ **Logging**: Never log sensitive environment variables
- ✅ **Backup**: Don't include .env in backups or snapshots

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

## Production Deployment

### Environment Setup
- Use production-grade database (PostgreSQL, MySQL) instead of SQLite
- Set `FLASK_DEBUG=0` in production
- Use environment-specific configuration files
- Implement proper logging and monitoring
- Set up SSL/TLS certificates
- Configure CORS properly for your frontend domain

### Security Considerations
- Use a web server like Gunicorn or uWSGI
- Implement rate limiting
- Set up proper firewall rules
- Regular security updates
- Monitor for vulnerabilities

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
