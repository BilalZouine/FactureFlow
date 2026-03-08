import time
from flask import request


def should_skip_logging(path: str) -> bool:
    skip_prefixes = (
        "/static/"
        "/favicon.ico",
    )

    skip_extensions = (
        ".js",
        ".css",
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".ico",
        ".map",
        ".webp",
        ".woff",
        ".woff2",
        ".ttf",
    )

    if path.startswith(skip_prefixes):
        return True

    if path.endswith(skip_extensions):
        return True

    return False


def register_request_logging(app, logger):
    @app.before_request
    def start_timer():
        request._start_time = time.time()

    @app.after_request
    def log_request(response):
        try:
            path = request.path or "/"

            if should_skip_logging(path):
                return response

            start_time = getattr(request, "_start_time", time.time())
            duration_ms = round((time.time() - start_time) * 1000, 2)

            forwarded_for = request.headers.get("X-Forwarded-For", "")
            ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.remote_addr

            logger.info(
                "%s | %s %s | %s | %sms",
                ip,
                request.method,
                path,
                response.status_code,
                duration_ms,
            )

        except Exception:
            logger.exception("Request logging failure")

        return response