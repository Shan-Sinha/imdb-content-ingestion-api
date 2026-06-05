"""Integration tests for GET /api/v1/movies."""

import pytest

AUTH_HEADERS = {"X-API-Key": "test_secret_key"}


@pytest.fixture()
def seeded_db(client, sample_csv):
    """Upload sample CSV so the movies collection has data for query tests."""
    with open(sample_csv, "rb") as f:
        data = {"file": (f, "test_movies.csv")}
        client.post(
            "/api/v1/upload",
            data=data,
            content_type="multipart/form-data",
            headers=AUTH_HEADERS,
        )


class TestListMovies:
    """Tests for the movies listing endpoint."""

    def test_default_pagination(self, client, seeded_db):
        """Default request should return paginated results."""
        response = client.get("/api/v1/movies", headers=AUTH_HEADERS)
        assert response.status_code == 200

        json_data = response.get_json()
        assert json_data["success"] is True
        assert "movies" in json_data["data"]
        assert "pagination" in json_data["data"]

        pagination = json_data["data"]["pagination"]
        assert pagination["current_page"] == 1
        assert pagination["per_page"] == 10
        assert pagination["total_records"] == 5

    def test_custom_per_page(self, client, seeded_db):
        """Should respect per_page parameter."""
        response = client.get("/api/v1/movies?per_page=2&page=1", headers=AUTH_HEADERS)
        json_data = response.get_json()

        assert len(json_data["data"]["movies"]) == 2
        assert json_data["data"]["pagination"]["has_next"] is True

    def test_page_2(self, client, seeded_db):
        """Requesting page 2 with per_page=2 should return next results."""
        response = client.get("/api/v1/movies?per_page=2&page=2", headers=AUTH_HEADERS)
        json_data = response.get_json()

        assert len(json_data["data"]["movies"]) == 2
        assert json_data["data"]["pagination"]["has_prev"] is True

    def test_filter_by_year(self, client, seeded_db):
        """Filtering by year=1995 should exclude 1976 and 1994 movies."""
        response = client.get("/api/v1/movies?year=1995", headers=AUTH_HEADERS)
        json_data = response.get_json()

        movies = json_data["data"]["movies"]
        # Sample data has 3 movies from 1995: Toy Story, Jumanji, La Haine
        assert json_data["data"]["pagination"]["total_records"] == 3
        for movie in movies:
            assert movie["year"] == 1995

    def test_filter_by_language(self, client, seeded_db):
        """Filtering by language=English should return only English movies."""
        response = client.get("/api/v1/movies?language=English", headers=AUTH_HEADERS)
        json_data = response.get_json()

        movies = json_data["data"]["movies"]
        # Toy Story, Jumanji, Taxi Driver have English
        assert json_data["data"]["pagination"]["total_records"] == 3
        for movie in movies:
            assert "English" in movie["languages"]

    def test_filter_by_language_case_insensitive(self, client, seeded_db):
        """Language filter should be case-insensitive."""
        response = client.get("/api/v1/movies?language=english", headers=AUTH_HEADERS)
        json_data = response.get_json()
        assert json_data["data"]["pagination"]["total_records"] == 3

    def test_filter_by_original_title(self, client, seeded_db):
        """Filtering by original_title should do case-insensitive substring matching."""
        # Query "toy" -> should match "Toy Story"
        response = client.get("/api/v1/movies?original_title=toy", headers=AUTH_HEADERS)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["data"]["pagination"]["total_records"] == 1
        assert json_data["data"]["movies"][0]["original_title"] == "Toy Story"

        # Query "man" -> should match "Jumanji"
        response = client.get("/api/v1/movies?original_title=man", headers=AUTH_HEADERS)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["data"]["pagination"]["total_records"] == 1
        assert json_data["data"]["movies"][0]["original_title"] == "Jumanji"

    def test_sort_by_vote_average_desc(self, client, seeded_db):
        """Movies should be sorted by vote_average descending."""
        response = client.get(
            "/api/v1/movies?sort_by=vote_average&order=desc",
            headers=AUTH_HEADERS
        )
        json_data = response.get_json()
        movies = json_data["data"]["movies"]

        ratings = [m["vote_average"] for m in movies]
        assert ratings == sorted(ratings, reverse=True)

    def test_sort_by_vote_average_asc(self, client, seeded_db):
        """Movies should be sorted by vote_average ascending."""
        response = client.get(
            "/api/v1/movies?sort_by=vote_average&order=asc",
            headers=AUTH_HEADERS
        )
        json_data = response.get_json()
        movies = json_data["data"]["movies"]

        ratings = [m["vote_average"] for m in movies]
        assert ratings == sorted(ratings)

    def test_sort_by_release_date_asc(self, client, seeded_db):
        """Movies should be sorted by release_date ascending."""
        response = client.get(
            "/api/v1/movies?sort_by=release_date&order=asc",
            headers=AUTH_HEADERS
        )
        json_data = response.get_json()
        movies = json_data["data"]["movies"]

        dates = [m["release_date"] for m in movies]
        assert dates == sorted(dates)

    def test_sort_by_release_date_desc(self, client, seeded_db):
        """Movies should be sorted by release_date descending."""
        response = client.get(
            "/api/v1/movies?sort_by=release_date&order=desc",
            headers=AUTH_HEADERS
        )
        json_data = response.get_json()
        movies = json_data["data"]["movies"]

        dates = [m["release_date"] for m in movies]
        assert dates == sorted(dates, reverse=True)

    def test_combined_filter_and_sort(self, client, seeded_db):
        """Filter by year + sort by rating should work together."""
        response = client.get(
            "/api/v1/movies?year=1995&sort_by=vote_average&order=desc",
            headers=AUTH_HEADERS
        )
        json_data = response.get_json()
        movies = json_data["data"]["movies"]

        # All from 1995
        for movie in movies:
            assert movie["year"] == 1995

        # Sorted by rating desc
        ratings = [m["vote_average"] for m in movies]
        assert ratings == sorted(ratings, reverse=True)

    def test_empty_result(self, client, seeded_db):
        """Filtering for a non-existent year should return empty list."""
        response = client.get("/api/v1/movies?year=2099", headers=AUTH_HEADERS)
        json_data = response.get_json()

        assert json_data["data"]["movies"] == []
        assert json_data["data"]["pagination"]["total_records"] == 0
        assert json_data["data"]["pagination"]["total_pages"] == 0

    def test_invalid_page(self, client, seeded_db):
        """Non-integer page should return 400."""
        response = client.get("/api/v1/movies?page=abc", headers=AUTH_HEADERS)
        assert response.status_code == 400

    def test_invalid_per_page(self, client, seeded_db):
        """per_page > 100 should return 400."""
        response = client.get("/api/v1/movies?per_page=999", headers=AUTH_HEADERS)
        assert response.status_code == 400

    def test_invalid_sort_by(self, client, seeded_db):
        """Unrecognised sort_by field should return 400."""
        response = client.get("/api/v1/movies?sort_by=budget", headers=AUTH_HEADERS)
        assert response.status_code == 400

    def test_invalid_order(self, client, seeded_db):
        """Invalid order value should return 400."""
        response = client.get("/api/v1/movies?order=sideways", headers=AUTH_HEADERS)
        assert response.status_code == 400

    def test_invalid_year(self, client, seeded_db):
        """Non-integer year should return 400."""
        response = client.get("/api/v1/movies?year=abc", headers=AUTH_HEADERS)
        assert response.status_code == 400

    def test_movie_response_shape(self, client, seeded_db):
        """Each movie in the response should have the expected fields."""
        response = client.get("/api/v1/movies?per_page=1", headers=AUTH_HEADERS)
        json_data = response.get_json()
        movie = json_data["data"]["movies"][0]

        expected_fields = {
            "id", "budget", "homepage", "original_language",
            "original_title", "overview", "release_date", "year",
            "revenue", "runtime", "status", "title", "vote_average",
            "vote_count", "production_company_id", "genre_id",
            "languages", "created_at",
        }
        assert expected_fields.issubset(set(movie.keys()))
        assert "_id" not in movie  # Should be renamed to 'id'
