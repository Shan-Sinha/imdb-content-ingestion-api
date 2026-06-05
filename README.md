# IMDb Content Upload & Review System

A RESTful API service built with **Python Flask** and **MongoDB** that allows the content team to upload movie data via CSV files and query the catalog with pagination, filtering, and sorting.

## Features

- **CSV Upload** — Bulk-upload movie data from CSV files (supports files up to 1 GB via chunked streaming)
- **Paginated Listing** — Browse all movies with configurable page size
- **Filtering** — Filter movies by year of release and language
- **Sorting** — Sort by release date or ratings (ascending/descending)
- **Robust Error Handling** — Consistent JSON error responses with descriptive messages

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | Python Flask |
| Database  | MongoDB |
| CSV Processing | Pandas (chunked reader) |
| Testing   | Pytest |

## Prerequisites

- **Python** 3.9 or higher
- **MongoDB** 4.4 or higher (running locally on default port `27017`)
- **pip** (Python package manager)

## Setup & Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd imdb
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
cp .env.example .env
```

Edit `.env` if your MongoDB is running on a non-default host/port:

```env
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=imdb
FLASK_DEBUG=1
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
* **`http://localhost:5000/docs`** (or simply go to the root url **`http://localhost:5000/`** which will redirect you there).

---

## API Documentation

### 1. Generate Authentication Token

**`POST /api/v1/auth/token`**

Generate a signed, timed Bearer token valid for 1 hour using your credentials.

**Request Body (JSON):**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Request Example:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}' \
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

---

### 2. Upload CSV

**`POST /api/v1/upload`**

Upload a CSV file containing movie data. The file is validated (checking that all required columns from the original file exist) and processed in chunks of 5,000 rows.

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

**Error Response (400 - Invalid Schema/Format):**
```json
{
    "success": false,
    "message": "CSV format is incorrect. Missing columns: languages",
    "data": null
}
```

---

### 3. List Movies

**`GET /api/v1/movies`**

Retrieve movies with pagination, filtering, and sorting.

**Query Parameters:**

| Parameter  | Type   | Default        | Description |
|-----------|--------|----------------|-------------|
| `page`     | int    | `1`            | Page number (1-based) |
| `per_page` | int    | `10`           | Items per page (max: 100) |
| `year`     | int    | —              | Filter by release year |
| `language` | string | —              | Filter by language (case-insensitive) |
| `original_title` | string | —        | Filter by original title (case-insensitive substring match) |
| `sort_by`  | string | `release_date` | Sort field: `release_date` or `vote_average` |
| `order`    | string | `desc`         | Sort order: `asc` or `desc` |

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

The test suite uses **pytest** and requires a running MongoDB instance. Tests use a separate database (`imdb_test`) that is automatically cleaned up.

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_upload.py::TestUploadCSV::test_upload_valid_csv PASSED
tests/test_upload.py::TestUploadCSV::test_upload_empty_csv PASSED
tests/test_upload.py::TestUploadCSV::test_upload_non_csv_file PASSED
...
tests/test_movies.py::TestListMovies::test_default_pagination PASSED
tests/test_movies.py::TestListMovies::test_filter_by_year PASSED
...
```

---

## Project Structure

```
imdb/
├── app/
│   ├── __init__.py          # Flask app factory, MongoDB setup, indexes
│   ├── config.py            # Configuration management
│   ├── models/
│   │   └── movie.py         # Movie document serializer
│   ├── routes/
│   │   ├── upload.py        # POST /api/v1/upload
│   │   └── movies.py        # GET  /api/v1/movies
│   ├── services/
│   │   ├── csv_service.py   # Chunked CSV processing & bulk insert
│   │   └── movie_service.py # Query builder (filter/sort/paginate)
│   └── utils/
│       ├── validators.py    # Input validation helpers
│       └── responses.py     # Standardised JSON responses
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_upload.py       # Upload API tests
│   └── test_movies.py       # Listing API tests
├── requirements.txt         # Python dependencies
├── run.py                   # Entry point
├── .env.example             # Environment variable template
└── README.md                # This file
```

## Design Decisions

### Handling Large CSV Files (up to 1 GB)
The CSV is **never loaded entirely into memory**. Instead, `pandas.read_csv()` reads the file in configurable chunks (default: 5,000 rows). Each chunk is transformed and bulk-inserted into MongoDB via `insert_many()`, keeping memory usage constant regardless of file size.

### MongoDB Indexes
Indexes are created on application startup for the fields used in filtering and sorting:
- `year` — for year-of-release filtering
- `languages` — multikey index for language filtering
- `release_date`, `vote_average` — for sorting
- Compound indexes (`year + release_date`, `year + vote_average`, etc.) — for combined filter + sort queries

### Data Transformation
- `release_date` strings are parsed into `datetime` objects for proper date sorting
- A `year` integer field is derived for efficient year-based filtering
- `languages` strings (e.g., `"['English', 'Français']"`) are parsed into native arrays for MongoDB multikey indexing
