# IMDb Content Upload & Review System

A RESTful API service built with **Python Flask** and **MongoDB** that allows the content team to upload movie data via CSV files and query the catalog with pagination, filtering, and sorting. The system follows **SOLID principles** with a full repository/service layer, dependency injection, and JWT-style Bearer token authentication backed by a MongoDB `users` collection.

## Features

- **User Registration** — Register users with securely hashed passwords (PBKDF2-SHA256)
- **Token Authentication** — Generate timed Bearer tokens (1 hour) verified against the database
- **CSV Upload** — Bulk-upload movie data from CSV files (supports files up to 1 GB via chunked streaming)
- **Paginated Listing** — Browse all movies with configurable page size
- **Filtering** — Filter movies by year, language, or original title (case-insensitive substring match)
- **Sorting** — Sort by release date or rating (ascending/descending)
- **Interactive Docs** — IMDb dark-themed Swagger UI at `/docs`
- **SOLID Architecture** — Repository interfaces, service abstractions, and dependency injection throughout

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | Python Flask |
| Database  | MongoDB |
| CSV Processing | Pandas (chunked reader) |
| Password Hashing | Werkzeug (PBKDF2-SHA256) |
| Testing   | Pytest |

## Prerequisites

- **Python** 3.9 or higher
- **MongoDB** 4.4 or higher (running locally on default port `27017`)
- **pip** (Python package manager)

## Setup & Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-folder>
```

> The folder name depends on how you cloned the repo. Use whatever directory name `git clone` created (e.g. `imdb-content-ingestion-api`).

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
cp .env.example .env
```

Edit `.env` if your MongoDB is running on a non-default host/port:

```env
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=imdb
FLASK_DEBUG=1
SECRET_KEY=your_secret_key_here
```

### 5. Start MongoDB

Ensure MongoDB is running. On most systems:

```bash
# If installed as a service, it may already be running
mongod
```

### 6. Run the server

```bash
python run.py
```

The server starts at `http://localhost:5000`.

To view the interactive Swagger API documentation and test the endpoints directly in your browser, open:
* **`http://localhost:5000/docs`** (or simply go to the root URL **`http://localhost:5000/`** which will redirect you there).

---

## API Documentation

> **Authentication flow**: Register a user → generate a token → use the token as a `Bearer` header on protected endpoints.

---

### 1. Register a User

**`POST /api/v1/users`** — *No authentication required*

Create a new user account. The password is securely hashed before storage and is never stored in plain text.

**Request Body (JSON):**
```json
{
  "username": "john_doe",
  "password": "secret_pass_123"
}
```

**Request Example:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"secret_pass_123"}' \
  http://localhost:5000/api/v1/users
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully.",
  "data": {
    "id": "65bfa78a2e1d7a8d54231b23",
    "username": "john_doe"
  }
}
```

**Error Response (400 — username already taken):**
```json
{
  "success": false,
  "message": "User with username 'john_doe' already exists.",
  "data": null
}
```

---

### 2. Generate Authentication Token

**`POST /api/v1/auth/token`** — *No authentication required*

Generate a signed Bearer token valid for **1 hour** using the credentials you registered with.

**Request Body (JSON):**
```json
{
  "username": "john_doe",
  "password": "secret_pass_123"
}
```

**Request Example:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"secret_pass_123"}' \
  http://localhost:5000/api/v1/auth/token
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Token generated successfully.",
  "data": {
    "token": "eyJhbGciOi...",
    "expires_in": 3600,
    "token_type": "Bearer"
  }
}
```

**Error Response (401 — wrong credentials):**
```json
{
  "success": false,
  "message": "Unauthorized: Invalid username or password.",
  "data": null
}
```

---

### 3. Upload CSV

**`POST /api/v1/upload`** — *Authentication required*

Upload a CSV file containing movie data. The file is validated (all required columns must be present) and processed in chunks of 5,000 rows.

**Request:**
```bash
curl -X POST \
  -H "Authorization: Bearer <your_token>" \
  -F "file=@movies_data_assignment.csv" \
  http://localhost:5000/api/v1/upload
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "CSV uploaded and processed successfully.",
  "data": {
    "records_inserted": 45534
  }
}
```

**Error Response (400 — Invalid Schema/Format):**
```json
{
  "success": false,
  "message": "CSV format is incorrect. Missing columns: languages",
  "data": null
}
```

---

### 4. List Movies

**`GET /api/v1/movies`** — *Authentication required*

Retrieve movies with pagination, filtering, and sorting.

**Query Parameters:**

| Parameter        | Type   | Default        | Description |
|-----------------|--------|----------------|-------------|
| `page`           | int    | `1`            | Page number (1-based) |
| `per_page`       | int    | `10`           | Items per page (max: 100) |
| `year`           | int    | —              | Filter by release year |
| `language`       | string | —              | Filter by language (case-insensitive) |
| `original_title` | string | —              | Filter by original title (case-insensitive substring match) |
| `sort_by`        | string | `release_date` | Sort field: `release_date` or `vote_average` |
| `order`          | string | `desc`         | Sort order: `asc` or `desc` |

**Example Requests:**

```bash
# Basic paginated listing
curl -H "Authorization: Bearer <your_token>" "http://localhost:5000/api/v1/movies?page=1&per_page=5"

# Filter by year
curl -H "Authorization: Bearer <your_token>" "http://localhost:5000/api/v1/movies?year=1995"

# Filter by language
curl -H "Authorization: Bearer <your_token>" "http://localhost:5000/api/v1/movies?language=English"

# Search by original title (case-insensitive substring)
curl -H "Authorization: Bearer <your_token>" "http://localhost:5000/api/v1/movies?original_title=toy"

# Sort by rating (highest first)
curl -H "Authorization: Bearer <your_token>" "http://localhost:5000/api/v1/movies?sort_by=vote_average&order=desc"

# Combined: 1995 English movies, sorted by rating
curl -H "Authorization: Bearer <your_token>" "http://localhost:5000/api/v1/movies?year=1995&language=English&sort_by=vote_average&order=desc&per_page=5"
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Movies fetched successfully.",
  "data": {
    "movies": [
      {
        "id": "684182...",
        "title": "Toy Story",
        "original_title": "Toy Story",
        "original_language": "en",
        "overview": "Led by Woody...",
        "release_date": "1995-10-30T00:00:00",
        "year": 1995,
        "budget": 30000000.0,
        "revenue": 373554033.0,
        "runtime": 81,
        "status": "Released",
        "vote_average": 7.7,
        "vote_count": 5415,
        "production_company_id": 3,
        "genre_id": 16,
        "homepage": "http://toystory.disney.com/toy-story",
        "languages": ["English"],
        "created_at": "2026-06-05T09:30:00"
      }
    ],
    "pagination": {
      "current_page": 1,
      "per_page": 10,
      "total_records": 45534,
      "total_pages": 4554,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

## Running Tests

The test suite uses **pytest** and requires a running MongoDB instance. Tests use a separate database (`imdb_test`) that is automatically cleaned up after each run.

```bash
# Windows
venv\Scripts\python -m pytest tests/ -v

# macOS/Linux
venv/bin/python -m pytest tests/ -v
```

Expected output:
```
tests/test_auth.py::test_register_user_success PASSED
tests/test_auth.py::test_register_user_duplicate_username PASSED
tests/test_auth.py::test_generate_token_success PASSED
...
tests/test_upload.py::TestUploadCSV::test_upload_valid_csv PASSED
tests/test_movies.py::TestListMovies::test_default_pagination PASSED
...
45 passed in 3.47s
```

---

## Project Structure

```
<repository-folder>/
├── app/
│   ├── __init__.py              # Flask app factory — wires repos, services, and blueprints
│   ├── config.py                # Configuration management
│   ├── models/
│   │   ├── movie.py             # Movie document model (from_mongo / to_dict)
│   │   └── user.py              # User model (password hash excluded from output)
│   ├── repositories/            # Data access layer (SOLID DIP)
│   │   ├── base_repository.py   # Abstract IRepository interface
│   │   ├── movie_repository.py  # IMovieRepository + MongoMovieRepository
│   │   └── user_repository.py   # IUserRepository + MongoUserRepository
│   ├── services/                # Business logic layer (SOLID SRP + ISP)
│   │   ├── interfaces.py        # IMovieService, ICSVService, IAuthService contracts
│   │   ├── csv_service.py       # Chunked CSV processing & bulk insert
│   │   ├── movie_service.py     # Query builder (filter/sort/paginate)
│   │   └── auth_service.py      # User registration, password hashing, token delegation
│   ├── routes/
│   │   ├── users.py             # POST /api/v1/users  (registration)
│   │   ├── auth.py              # POST /api/v1/auth/token
│   │   ├── upload.py            # POST /api/v1/upload
│   │   ├── movies.py            # GET  /api/v1/movies
│   │   ├── docs.py              # GET  /docs  (Swagger UI)
│   │   └── swagger.json         # OpenAPI 3.0.0 specification
│   ├── templates/
│   │   └── swagger_ui.html      # Swagger UI HTML template
│   ├── static/
│   │   └── css/
│   │       └── swagger_ui.css   # Custom IMDb dark theme stylesheet
│   └── utils/
│       ├── auth.py              # TokenAuthenticator class + @require_auth decorator
│       ├── validators.py        # Input validation helpers
│       └── responses.py         # Standardised JSON response envelope
├── tests/
│   ├── conftest.py              # Pytest fixtures (app, client, sample CSV)
│   ├── test_auth.py             # Registration, login, and access control tests
│   ├── test_docs.py             # Swagger UI and spec endpoint tests
│   ├── test_movies.py           # Listing, filtering, and sorting tests
│   ├── test_oop.py              # SOLID class instantiation tests
│   └── test_upload.py           # CSV upload and schema validation tests
├── requirements.txt             # Python dependencies
├── run.py                       # Entry point
├── .env.example                 # Environment variable template
└── README.md                    # This file
```

---

## Design Decisions

### SOLID Architecture
The codebase is structured around SOLID principles:
- **SRP**: Repositories handle data access, services handle business logic, routes handle HTTP concerns — each with a single responsibility.
- **OCP**: New database backends (e.g. PostgreSQL) can be swapped in by implementing the existing repository interfaces without touching service or route code.
- **DIP**: Services depend on abstract interfaces (`IMovieRepository`, `IUserRepository`), not concrete PyMongo classes. The app factory (`create_app`) wires concrete implementations at startup.

### Password Security
Passwords are hashed using **PBKDF2-SHA256** via `werkzeug.security` (a built-in Flask dependency). Raw passwords are never stored or logged. The `User.to_dict()` method explicitly excludes the `password_hash` field from all API responses.

### Handling Large CSV Files (up to 1 GB)
The CSV is **never loaded entirely into memory**. Instead, `pandas.read_csv()` reads the file in configurable chunks (default: 5,000 rows). Each chunk is transformed and bulk-inserted into MongoDB via `insert_many()`, keeping memory usage constant regardless of file size.

### MongoDB Indexes
Indexes are created on application startup (idempotent) for the fields used in filtering and sorting:
- `year`, `languages`, `release_date`, `vote_average` — single-field indexes
- Compound indexes (`year + release_date`, `year + vote_average`, etc.) — for combined filter + sort queries
- `username` (unique) — enforces unique usernames in the `users` collection
