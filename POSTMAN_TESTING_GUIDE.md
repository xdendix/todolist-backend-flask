# Postman Testing Guide for TodoList Flask API

## Base URL
```
http://127.0.0.1:5000
```

## API Endpoints

### 1. Health Check
**GET** `/health`

**Response:**
```json
{
  "status": "ok"
}
```

---

### 2. Get All Todos
**GET** `/api/todos/`

**Response:**
```json
[
  {
    "id": 1,
    "judul": "Test Todo",
    "status": false,
    "prioritas": "High",
    "deadline": null,
    "created_at": "2025-09-02T09:43:04.021936",
    "updated_at": null
  }
]
```

---

### 3. Create New Todo
**POST** `/api/todos/`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "judul": "Belajar Flask",
  "prioritas": "High",
  "status": false,
  "deadline": "2025-12-31"
}
```

**Response:**
```json
{
  "id": 2,
  "judul": "Belajar Flask",
  "status": false,
  "prioritas": "High",
  "deadline": "2025-12-31",
  "created_at": "2025-09-02T09:47:15.123456",
  "updated_at": null
}
```

---

### 4. Get Todo by ID
**GET** `/api/todos/{id}`

**Example:** `/api/todos/1`

**Response:**
```json
{
  "id": 1,
  "judul": "Test Todo",
  "status": false,
  "prioritas": "High",
  "deadline": null,
  "created_at": "2025-09-02T09:43:04.021936",
  "updated_at": null
}
```

---

### 5. Update Todo
**PUT** `/api/todos/{id}`

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "judul": "Updated Todo Title",
  "status": true,
  "prioritas": "Medium"
}
```

**Response:**
```json
{
  "id": 1,
  "judul": "Updated Todo Title",
  "status": true,
  "prioritas": "Medium",
  "deadline": null,
  "created_at": "2025-09-02T09:43:04.021936",
  "updated_at": "2025-09-02T09:48:30.654321"
}
```

---

### 6. Delete Todo
**DELETE** `/api/todos/{id}`

**Example:** `/api/todos/1`

**Response:** `204 No Content` (empty body)

---

### 7. Search Todos
**GET** `/api/todos/search`

**Query Parameters:**
- `q`: Search keyword in title (case insensitive)
- `prioritas`: Filter by priority (High/Medium/Low)
- `status`: Filter by status (selesai/belum selesai)
- `deadline`: Filter by deadline (YYYY-MM-DD)

**Examples:**

**Search by keyword:**
```
GET /api/todos/search?q=flask
```

**Search by priority:**
```
GET /api/todos/search?prioritas=High
```

**Search by status:**
```
GET /api/todos/search?status=selesai
```

**Combined search:**
```
GET /api/todos/search?q=belajar&prioritas=High&status=belum selesai
```

**Response:**
```json
[
  {
    "id": 2,
    "judul": "Belajar Flask",
    "status": false,
    "prioritas": "High",
    "deadline": "2025-12-31",
    "created_at": "2025-09-02T09:47:15.123456",
    "updated_at": null
  }
]
```

---

## Validation Rules

### Required Fields
- `judul`: Must not be empty or whitespace only

### Optional Fields
- `prioritas`: Must be "High", "Medium", or "Low" (case insensitive)
- `status`: Boolean (true/false)
- `deadline`: Date in YYYY-MM-DD format

### Validation Error Examples

**Empty title:**
```json
{
  "judul": ["Judul tidak boleh kosong."]
}
```

**Invalid priority:**
```json
{
  "prioritas": ["Prioritas hanya boleh High, Medium, atau Low."]
}
```

**Invalid deadline format:**
```json
{
  "deadline": ["Format deadline tidak valid (gunakan YYYY-MM-DD)."]
}
```

---

## Postman Collection Setup

1. **Create New Collection** in Postman
2. **Set Base URL** as variable:
   - Variable name: `base_url`
   - Initial value: `http://127.0.0.1:5000`
   - Current value: `http://127.0.0.1:5000`

3. **Import or Create Requests** for each endpoint above

4. **Test Scenarios to Try:**

   **Happy Path:**
   - Create todo → Get all todos → Update todo → Search todos → Delete todo

   **Error Cases:**
   - Create todo with empty title
   - Create todo with invalid priority
   - Get non-existent todo ID
   - Update non-existent todo ID
   - Delete non-existent todo ID

   **Edge Cases:**
   - Create todo with only required fields
   - Create todo with all fields
   - Update with partial data
   - Search with multiple filters

---

## Sample Postman Tests

You can add these test scripts in Postman's "Tests" tab:

**For Create/Update operations:**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Response has required fields", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('judul');
    pm.expect(jsonData).to.have.property('created_at');
});
```

**For GET operations:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response is array", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.be.an('array');
});
```

**For DELETE operations:**
```javascript
pm.test("Status code is 204", function () {
    pm.response.to.have.status(204);
});
```

---

## Running the Flask App

Make sure your Flask app is running before testing:

```bash
cd /home/xdendix/Documents/Programming/todolist-backend-flask
source todolist_backend_venv/bin/activate
python app.py
```

The app will be available at: `http://127.0.0.1:5000`

---

## Notes

- All endpoints return JSON responses
- Date fields use ISO format (YYYY-MM-DDTHH:MM:SS.microseconds)
- Boolean fields use `true`/`false` (not strings)
- Error responses include detailed validation messages in Indonesian
- The API supports both PUT and PATCH for updates (both work the same way)
