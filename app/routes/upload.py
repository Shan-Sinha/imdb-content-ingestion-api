"""CSV upload endpoint.

POST /api/v1/upload
    - Accepts multipart/form-data with a 'file' field
    - Validates extension (.csv)
    - Streams to disk, processes in chunks, inserts into MongoDB
"""

import logging
import os

from flask import Blueprint, current_app, request
from werkzeug.utils import secure_filename

from app.utils.auth import require_auth
from app.utils.responses import success_response, error_response
from app.utils.validators import allowed_file

logger = logging.getLogger(__name__)

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
@require_auth
def upload_csv():
    """Handle CSV file upload."""

    # --- Check that a file was included ---
    if "file" not in request.files:
        return error_response("No file part in the request.", 400)

    file = request.files["file"]

    if file.filename == "" or file.filename is None:
        return error_response("No file selected for upload.", 400)

    # --- Validate file extension ---
    if not allowed_file(file.filename):
        return error_response(
            "Invalid file format. Only CSV files are accepted.", 400
        )

    # --- Save to temp location ---
    filename = secure_filename(file.filename)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    filepath = os.path.join(upload_folder, filename)

    try:
        file.save(filepath)
        logger.info("File saved to %s", filepath)

        # --- Process and insert (OOP) ---
        from app.services.csv_service import CSVService
        collection = current_app.db["movies"]
        chunk_size = current_app.config.get("CSV_CHUNK_SIZE", 5000)
        
        csv_service = CSVService(collection, chunk_size)
        total = csv_service.process(filepath)

        return success_response(
            data={"records_inserted": total},
            message="CSV uploaded and processed successfully.",
        )
    except ValueError as exc:
        logger.warning("CSV validation error: %s", exc)
        return error_response(str(exc), 400)
    except Exception as exc:
        logger.exception("Error processing CSV upload")
        return error_response(
            f"Failed to process CSV: {str(exc)}", 500
        )
    finally:
        # Always clean up the temp file
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info("Temp file removed: %s", filepath)
