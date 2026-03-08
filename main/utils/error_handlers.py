import traceback
from flask import jsonify, request

from main.utils.errors import AppError
from main.utils.response import server_error


def register_error_handlers(app, logger):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        logger.warning(
            "APP_ERROR | %s %s | %s",
            request.method,
            request.path,
            str(error),
        )
        return error.to_response()

    @app.errorhandler(404)
    def handle_404(error):
        logger.warning(
            "404 | %s %s | %s",
            request.method,
            request.path,
            str(error),
        )
        return jsonify({
            "status": "error",
            "error_code": "NOT_FOUND",
            "message": str(error)
        }), 404

    @app.errorhandler(405)
    def handle_405(error):
        logger.warning(
            "405 | %s %s | %s",
            request.method,
            request.path,
            str(error),
        )
        return jsonify({
            "status": "error",
            "error_code": "METHOD_NOT_ALLOWED",
            "message": str(error)
        }), 405

    @app.errorhandler(413)
    def handle_413(error):
        logger.warning(
            "413 | %s %s | File exceeds 16 MB limit.",
            request.method,
            request.path,
        )
        return jsonify({
            "status": "error",
            "error_code": "FILE_TOO_LARGE",
            "message": "File exceeds 16 MB limit."
        }), 413

    @app.errorhandler(Exception)
    def handle_unexpected(error):
        logger.exception(
            "UNEXPECTED_ERROR | %s %s | %s",
            request.method,
            request.path,
            str(error),
        )
        traceback.print_exc()
        return server_error(
            "Unexpected error.",
            details={
                "type": type(error).__name__,
                "info": str(error)
            }
        )