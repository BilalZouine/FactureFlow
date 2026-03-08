from flask import Blueprint, request, send_file
from main.services.parser_service import parse_file
from main.services.invoice_service import build_invoice
from main.services.pdf_service import generate_pdf, safe_filename
from main.utils.counter import reset_counter, get_next_invoice_number
from main.utils.errors import (
    AppError,
    MissingFileError,
    EmptyFilenameError,
)
from main.utils.response import success, error

bp = Blueprint("routes", __name__)


@bp.route("/health")
def health():
    return success(
        {
            "service": "OMBJI TRANS Invoice Generator",
            "version": "1.0.0",
            "endpoints": [
                {"method": "GET", "path": "/", "desc": "Web UI"},
                {"method": "GET", "path": "/health", "desc": "Health check"},
                {"method": "POST", "path": "/generate", "desc": "Upload file -> PDF"},
                {"method": "POST", "path": "/counter/reset", "desc": "Reset invoice counter (optional)"},
            ],
        },
        message="Server is running",
    )


@bp.route("/generate", methods=["POST"])
def generate():
    """
    POST /generate  multipart/form-data: file, invoice_number (optional, default 1)
    Errors: 400 MISSING_FILE | EMPTY_FILENAME | UNSUPPORTED_FILE_TYPE |
                EMPTY_FILE   | MISSING_COLUMN
            422 NO_NUMERIC_DATA
            500 PDF_GENERATION_FAILED
    """
    if "file" not in request.files:
        raise MissingFileError()
    f = request.files["file"]
    if not f.filename:
        raise EmptyFilenameError()
    df, col_map = parse_file(f)
    num = get_next_invoice_number()
    if num < 1:
        num = 1
    inv = build_invoice(df, col_map, num)
    pdf = generate_pdf(inv)
    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=safe_filename(inv),
    )


@bp.route("/counter/reset", methods=["POST"])
def counter_reset():
    """POST /counter/reset?start=N — optional admin."""
    try:
        start = int(request.args.get("start", 0))
    except ValueError:
        return error("'start' must be an integer.")
    n = reset_counter(start)
    return success({"counter": n}, message=f"Counter reset to {n}")
