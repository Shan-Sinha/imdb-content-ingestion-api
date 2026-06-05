"""Integration tests for POST /api/v1/upload."""

import io

AUTH_HEADERS = {"X-API-Key": "test_secret_key"}


class TestUploadCSV:
    """Tests for the CSV upload endpoint."""

    def test_upload_valid_csv(self, client, sample_csv, db):
        """Uploading a valid CSV should insert all rows and return count."""
        with open(sample_csv, "rb") as f:
            data = {"file": (f, "test_movies.csv")}
            response = client.post(
                "/api/v1/upload",
                data=data,
                content_type="multipart/form-data",
                headers=AUTH_HEADERS,
            )

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["success"] is True
        assert json_data["data"]["records_inserted"] == 5

        # Verify data landed in MongoDB
        count = db["movies"].count_documents({})
        assert count == 5

    def test_upload_empty_csv(self, client, empty_csv, db):
        """Uploading a CSV with only headers should insert 0 records."""
        with open(empty_csv, "rb") as f:
            data = {"file": (f, "empty_movies.csv")}
            response = client.post(
                "/api/v1/upload",
                data=data,
                content_type="multipart/form-data",
                headers=AUTH_HEADERS,
            )

        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["success"] is True
        assert json_data["data"]["records_inserted"] == 0

    def test_upload_invalid_csv_format(self, client):
        """Uploading a CSV file with incorrect headers should return 400."""
        # Missing 'languages' column
        bad_content = (
            "budget,homepage,original_language,original_title,overview,"
            "release_date,revenue,runtime,status,title,vote_average,"
            "vote_count,production_company_id,genre_id\n"
            "30000000.0,,en,Toy Story,A toy story,1995-10-30,373554033.0,"
            "81,Released,Toy Story,7.7,5415.0,3,16\n"
        )
        data = {"file": (io.BytesIO(bad_content.encode("utf-8")), "bad_format.csv")}
        response = client.post(
            "/api/v1/upload",
            data=data,
            content_type="multipart/form-data",
            headers=AUTH_HEADERS
        )
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data["success"] is False
        assert "Missing columns" in json_data["message"]

    def test_upload_non_csv_file(self, client, non_csv_file):
        """Uploading a non-CSV file should return 400."""
        with open(non_csv_file, "rb") as f:
            data = {"file": (f, "not_a_csv.txt")}
            response = client.post(
                "/api/v1/upload",
                data=data,
                content_type="multipart/form-data",
                headers=AUTH_HEADERS,
            )

        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data["success"] is False
        assert "CSV" in json_data["message"]

    def test_upload_no_file(self, client):
        """Request without a file field should return 400."""
        response = client.post(
            "/api/v1/upload",
            data={},
            content_type="multipart/form-data",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data["success"] is False

    def test_upload_no_filename(self, client):
        """File with empty filename should return 400."""
        data = {"file": (io.BytesIO(b""), "")}
        response = client.post(
            "/api/v1/upload",
            data=data,
            content_type="multipart/form-data",
            headers=AUTH_HEADERS,
        )

        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data["success"] is False

    def test_uploaded_data_has_correct_fields(self, client, sample_csv, db):
        """Verify that inserted documents have the expected shape."""
        with open(sample_csv, "rb") as f:
            data = {"file": (f, "test_movies.csv")}
            client.post(
                "/api/v1/upload",
                data=data,
                content_type="multipart/form-data",
                headers=AUTH_HEADERS,
            )

        doc = db["movies"].find_one({"title": "Toy Story"})
        assert doc is not None
        assert doc["budget"] == 30000000.0
        assert doc["original_language"] == "en"
        assert doc["year"] == 1995
        assert doc["vote_average"] == 7.7
        assert doc["runtime"] == 81
        assert doc["languages"] == ["English"]
        assert doc["release_date"] is not None

    def test_languages_parsed_correctly(self, client, sample_csv, db):
        """Multi-language strings should be parsed into lists."""
        with open(sample_csv, "rb") as f:
            data = {"file": (f, "test_movies.csv")}
            client.post(
                "/api/v1/upload",
                data=data,
                content_type="multipart/form-data",
                headers=AUTH_HEADERS,
            )

        doc = db["movies"].find_one({"title": "Jumanji"})
        assert doc is not None
        assert isinstance(doc["languages"], list)
        assert "English" in doc["languages"]
        assert "Français" in doc["languages"]
