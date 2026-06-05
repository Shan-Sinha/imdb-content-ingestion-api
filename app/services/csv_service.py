"""CSV processing service — chunked reading and bulk MongoDB insertion."""

import ast
import logging
from datetime import datetime, timezone
import pandas as pd

logger = logging.getLogger(__name__)


class CSVService:
    """Service to handle CSV files schema validation and bulk database loading."""

    REQUIRED_COLUMNS = [
        "budget", "homepage", "original_language", "original_title", "overview",
        "release_date", "revenue", "runtime", "status", "title",
        "vote_average", "vote_count", "production_company_id", "genre_id", "languages"
    ]

    def __init__(self, collection, chunk_size: int = 5000):
        """Initialize the CSV service with MongoDB collection and chunk size."""
        self.collection = collection
        self.chunk_size = chunk_size

    def validate_headers(self, filepath: str) -> None:
        """Validate that all required columns are present in the CSV file."""
        try:
            df_headers = pd.read_csv(filepath, nrows=0, keep_default_na=False, encoding="utf-8")
            actual_cols = list(df_headers.columns)
        except Exception as exc:
            raise ValueError(f"Unable to read CSV headers: {str(exc)}")

        missing_cols = set(self.REQUIRED_COLUMNS) - set(actual_cols)
        if missing_cols:
            raise ValueError(f"CSV format is incorrect. Missing columns: {', '.join(sorted(missing_cols))}")

    def process(self, filepath: str) -> int:
        """Read a CSV file in chunks, validate, and bulk-insert into MongoDB."""
        self.validate_headers(filepath)

        total_inserted = 0
        reader = pd.read_csv(
            filepath,
            chunksize=self.chunk_size,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8",
            on_bad_lines="skip",
        )

        for chunk_number, chunk_df in enumerate(reader, start=1):
            documents = self._transform_chunk(chunk_df)
            if documents:
                self.collection.insert_many(documents, ordered=False)
                total_inserted += len(documents)
                logger.info(
                    "Chunk %d: inserted %d records (total so far: %d)",
                    chunk_number, len(documents), total_inserted,
                )

        return total_inserted

    def _transform_chunk(self, df: pd.DataFrame) -> list[dict]:
        """Convert a DataFrame chunk into a list of MongoDB documents."""
        documents = []
        now = datetime.now(timezone.utc)

        for _, row in df.iterrows():
            try:
                doc = {
                    "budget": self._to_float(row.get("budget")),
                    "homepage": self._to_str_or_none(row.get("homepage")),
                    "original_language": self._to_str_or_none(row.get("original_language")),
                    "original_title": self._to_str_or_none(row.get("original_title")),
                    "overview": self._to_str_or_none(row.get("overview")),
                    "release_date": self._parse_date(row.get("release_date")),
                    "year": self._extract_year(row.get("release_date")),
                    "revenue": self._to_float(row.get("revenue")),
                    "runtime": self._to_int(row.get("runtime")),
                    "status": self._to_str_or_none(row.get("status")),
                    "title": self._to_str_or_none(row.get("title")),
                    "vote_average": self._to_float(row.get("vote_average")),
                    "vote_count": self._to_int(row.get("vote_count")),
                    "production_company_id": self._to_int(row.get("production_company_id")),
                    "genre_id": self._to_int(row.get("genre_id")),
                    "languages": self._parse_languages(row.get("languages")),
                    "created_at": now,
                }
                documents.append(doc)
            except Exception as exc:
                logger.warning("Skipping row due to error: %s", exc)

        return documents

    # Helper conversion methods
    @staticmethod
    def _to_float(value) -> float | None:
        if value is None or str(value).strip() == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _to_int(value) -> int | None:
        f = CSVService._to_float(value)
        if f is None:
            return None
        return int(f)

    @staticmethod
    def _to_str_or_none(value) -> str | None:
        if value is None:
            return None
        s = str(value).strip()
        return s if s else None

    @staticmethod
    def _parse_date(value) -> datetime | None:
        if not value or str(value).strip() == "":
            return None
        try:
            return datetime.strptime(str(value).strip(), "%Y-%m-%d")
        except ValueError:
            return None

    @staticmethod
    def _extract_year(value) -> int | None:
        dt = CSVService._parse_date(value)
        return dt.year if dt else None

    @staticmethod
    def _parse_languages(value) -> list[str]:
        if not value or str(value).strip() in ("", "[]"):
            return []
        try:
            parsed = ast.literal_eval(str(value).strip())
            if isinstance(parsed, list):
                return [str(lang).strip() for lang in parsed if str(lang).strip()]
            return []
        except (ValueError, SyntaxError):
            return []
