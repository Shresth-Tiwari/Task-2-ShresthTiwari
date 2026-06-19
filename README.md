# Task-2-ShresthTiwari — Flask + PostgreSQL REST API

A production-quality REST API built with **Flask**, **SQLAlchemy ORM**, and **PostgreSQL** that implements full **CRUD** operations on a `User` resource with duplicate prevention, validation, and pagination.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Flask 3.x |
| ORM | Flask-SQLAlchemy |
| Migrations | Flask-Migrate (Alembic) |
| Validation | Marshmallow |
| Database | PostgreSQL |
| CORS | Flask-CORS |

---

## Project Structure

```
Task-2-ShresthTiwari/
├── app/
│   ├── __init__.py          # App factory
│   ├── extensions.py        # SQLAlchemy, Migrate, CORS instances
│   ├── models.py            # User model
│   ├── schemas.py           # Marshmallow validation schemas
│   └── routes/
│       ├── __init__.py
│       └── users.py         # CRUD route handlers
├── config.py                # Dev/Prod config classes
├── run.py                   # Entry point
├── requirements.txt
├── .env.example             # Env variable template
└── .gitignore
```

---

## User Schema

| Field | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key, auto-increment |
| `username` | String(80) | **Unique**, Not Null, indexed |
| `email` | String(120) | **Unique**, Not Null, indexed |
| `full_name` | String(200) | Optional |
| `created_at` | DateTime | Auto-set on create |
| `updated_at` | DateTime | Auto-updated on modify |

---

## API Endpoints

| Method | Endpoint | Description | Success |
|---|---|---|---|
| `POST` | `/api/users` | Create a new user | `201` |
| `GET` | `/api/users` | Get all users (paginated) | `200` |
| `GET` | `/api/users/<id>` | Get a user by ID | `200` |
| `PUT` | `/api/users/<id>` | Update a user (partial) | `200` |
| `DELETE` | `/api/users/<id>` | Delete a user | `200` |

---

## Setup & Installation

### 1. Clone & enter directory

```bash
cd Task-2-ShresthTiwari
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
```

Edit `.env` with your PostgreSQL credentials:

```env
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/users_db
SECRET_KEY=your-secret-key
FLASK_ENV=development
FLASK_APP=run.py
```

### 5. Create the PostgreSQL database

```sql
CREATE DATABASE users_db;
```

### 6. Run database migrations

```bash
flask db init
flask db migrate -m "Initial user table"
flask db upgrade
```

### 7. Start the server

```bash
python run.py
```

The API will be live at `http://localhost:5000`.

---

## API Usage Examples

### Create a user

```bash
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe", "email": "john@example.com", "full_name": "John Doe"}'
```

**Response `201`:**
```json
{
  "message": "User created successfully.",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "created_at": "2025-01-01T12:00:00+00:00",
    "updated_at": "2025-01-01T12:00:00+00:00"
  }
}
```

### Get all users (with pagination)

```bash
curl http://localhost:5000/api/users?page=1&per_page=10
```

### Get a single user

```bash
curl http://localhost:5000/api/users/1
```

### Update a user

```bash
curl -X PUT http://localhost:5000/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Johnathan Doe"}'
```

### Delete a user

```bash
curl -X DELETE http://localhost:5000/api/users/1
```

---

## Duplicate Prevention

Duplicate entries are blocked at **two layers**:

1. **Application layer** — pre-check query returns `409 Conflict` with a descriptive message identifying which field (`username` or `email`) caused the conflict.
2. **Database layer** — unique constraints on `username` and `email` columns catch any race conditions via `IntegrityError`.

**Example `409` response:**
```json
{
  "error": "Conflict",
  "message": "Username 'johndoe' is already taken.",
  "field": "username"
}
```

---

## Error Responses

| Status | Meaning |
|---|---|
| `400` | Bad Request — invalid JSON or validation failure |
| `404` | Not Found — user ID does not exist |
| `405` | Method Not Allowed |
| `409` | Conflict — duplicate username or email |
| `500` | Internal Server Error |