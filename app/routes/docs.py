"""API Documentation routes blueprint."""

import json
import os
from flask import Blueprint, Response, redirect, render_template

docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/")
def index():
    """Redirect root to /docs."""
    return redirect("/docs")


@docs_bp.route("/docs")
def swagger_ui():
    """Serve the Swagger UI documentation page using templates and static files."""
    return render_template("swagger_ui.html")


@docs_bp.route("/api/v1/swagger.json")
def get_swagger_json():
    """Serve the OpenAPI specification."""
    spec_path = os.path.join(os.path.dirname(__file__), "swagger.json")
    try:
        with open(spec_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Response(json.dumps(data), mimetype="application/json")
    except Exception as exc:
        return Response(
            json.dumps({"error": f"Failed to load spec: {str(exc)}"}),
            status=500,
            mimetype="application/json",
        )
