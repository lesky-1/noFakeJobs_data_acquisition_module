
import os
import requests
import sys


JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")
JOOBLE_API_URL = "https://mx.jooble.org/api"


def search_jooble(criteria):

    if not JOOBLE_API_KEY:
        raise RuntimeError(
            "No se encontró la variable JOOBLE_API_KEY"
        )

    position = criteria.get("position", "")

    location_parts = []

    if criteria.get("city"):
        location_parts.append(
            criteria["city"]
        )

    if criteria.get("state"):
        location_parts.append(
            criteria["state"]
        )

    location = ", ".join(location_parts)

    if not location:
        location = "México"

    payload = {
        "keywords": position,
        "location": location,
        "page": 1,
        "ResultOnPage": 20
    }

    if criteria.get("radiusKm"):
        payload["radius"] = str(
            criteria["radiusKm"]
        )

    if criteria.get("salaryMin"):
        payload["salary"] = criteria["salaryMin"]

    print(
        f"[Jooble] Buscando '{position}' "
        f"en '{location}'...",
        file=sys.stderr
    )

    response = requests.post(
        f"{JOOBLE_API_URL}/{JOOBLE_API_KEY}",
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Jooble respondió HTTP "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        )

    data = response.json()

    jobs = []

    for job in data.get("jobs", []):

        company = job.get("company")
        location_value = job.get("location")
        title = job.get("title")
        description = job.get("snippet")
        url = job.get("link")
        published_at = job.get("updated")

        jobs.append({
            "source": "jooble",

            "id": (
                str(job["id"])
                if job.get("id") is not None
                else None
            ),

            "title": (
                title
                if title
                else None
            ),

            "company": (
                company
                if company
                else None
            ),

            "location": (
                location_value
                if location_value
                else None
            ),

            "modality": None,

            "salaryMin": None,

            "salaryMax": None,

            "salaryCurrency": None,

            "salaryText": None,

            "description": (
                description
                if description
                else None
            ),

            "url": (
                url
                if url
                else ""
            ),

            "publishedAt": (
                published_at
                if published_at
                else None
            )
        })

    print(
        f"[Jooble] Ofertas encontradas: "
        f"{len(jobs)}",
        file=sys.stderr
    )

    return jobs
