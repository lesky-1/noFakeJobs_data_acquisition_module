import requests
import time


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/154.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.8"
}


def classify_status(status_code):

    if status_code == 200:
        return "success"

    if status_code == 401:
        return "unauthorized"

    if status_code == 403:
        return "blocked"

    if status_code == 404:
        return "not_found"

    if status_code == 429:
        return "rate_limited"

    if 500 <= status_code <= 599:
        return "server_error"

    return "error"


def fetch_page(url, timeout=20):

    start = time.perf_counter()

    try:

        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=timeout,
            allow_redirects=True
        )

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        access = classify_status(
            response.status_code
        )

        return {
            "success": response.status_code == 200,

            "access": access,

            "httpStatus": response.status_code,

            "message": (
                f"HTTP {response.status_code}"
            ),

            "html": response.text,

            "finalUrl": response.url,

            "elapsedMs": round(elapsed, 2)
        }

    except requests.exceptions.Timeout:

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        return {
            "success": False,
            "access": "timeout",
            "httpStatus": None,
            "message": "La solicitud agotó el tiempo de espera",
            "html": "",
            "finalUrl": url,
            "elapsedMs": round(elapsed, 2)
        }

    except requests.exceptions.ConnectionError as error:

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        return {
            "success": False,
            "access": "connection_error",
            "httpStatus": None,
            "message": f"Error de conexión: {error}",
            "html": "",
            "finalUrl": url,
            "elapsedMs": round(elapsed, 2)
        }

    except requests.exceptions.RequestException as error:

        elapsed = (
            time.perf_counter() - start
        ) * 1000

        return {
            "success": False,
            "access": "error",
            "httpStatus": None,
            "message": f"Error HTTP: {error}",
            "html": "",
            "finalUrl": url,
            "elapsedMs": round(elapsed, 2)
        }