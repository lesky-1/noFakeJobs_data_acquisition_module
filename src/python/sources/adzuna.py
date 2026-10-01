import os
import requests
import sys


ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs/mx/search"


def search_adzuna(criteria):

    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if not app_id:
        raise RuntimeError("No se encontró ADZUNA_APP_ID")

    if not app_key:
        raise RuntimeError("No se encontró ADZUNA_APP_KEY")

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": 20,
        "content-type": "application/json"
    }

    # =========================
    # FILTRO DE UBICACIÓN
    # =========================

    location_parts = []

    if criteria.get("city"):
        location_parts.append(criteria["city"])

    if criteria.get("state"):
        location_parts.append(criteria["state"])

    if location_parts:
        params["where"] = ", ".join(location_parts)

    # =========================
    # FILTRO DE PUESTO
    # =========================

    if criteria.get("position"):
        params["what"] = criteria["position"]

    # =========================
    # PETICIÓN
    # =========================

    print(
        "[Adzuna] Consultando ofertas...",
        file=sys.stderr
    )

    response = requests.get(
        f"{ADZUNA_API_URL}/1",
        params=params,
        timeout=30
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Adzuna respondió HTTP "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        )

    data = response.json()

    jobs = []

    # =========================
    # OFERTAS
    # =========================

    for job in data.get("results", []):

        location = job.get("location") or {}
        company = job.get("company") or {}
        category = job.get("category") or {}

        jobs.append({
            "source": "adzuna",

            "id": str(job["id"])
            if job.get("id") is not None
            else None,

            "title": job.get("title"),

            "company": company.get(
                "display_name"
            ),

            "location": location.get(
                "display_name"
            ),

            "latitude": job.get(
                "latitude"
            ),

            "longitude": job.get(
                "longitude"
            ),

            "category": category.get(
                "label"
            ),

            "categoryTag": category.get(
                "tag"
            ),

            "salaryMin": job.get(
                "salary_min"
            ),

            "salaryMax": job.get(
                "salary_max"
            ),

            "salaryPredicted": job.get(
                "salary_is_predicted"
            ),

            "contractType": job.get(
                "contract_type"
            ),

            "contractTime": job.get(
                "contract_time"
            ),

            "description": job.get(
                "description"
            ),

            "url": job.get(
                "redirect_url"
            ),

            "publishedAt": job.get(
                "created"
            )
        })

    print(
        f"[Adzuna] Ofertas encontradas: {len(jobs)}",
        file=sys.stderr
    )

    return jobs