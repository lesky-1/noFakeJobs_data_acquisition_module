
import sys
import json
import unicodedata

sys.stdout.reconfigure(
    encoding="utf-8"
)

sys.stderr.reconfigure(
    encoding="utf-8"
)

from sources.jooble import search_jooble
from sources.adzuna import search_adzuna
from sources.web_portals import scrape_html_portal
from sources.filters import (
    filter_jobs,
    deduplicate_jobs
)


def normalize_slug(text):
    text = text.strip().lower()

    text = unicodedata.normalize(
        "NFD",
        text
    )

    text = "".join(
        char
        for char in text
        if unicodedata.category(char) != "Mn"
    )

    text = text.replace(
        " ",
        "-"
    )

    return text


def get_computrabajo_url(criteria):

    city = criteria.get("city")

    if city:

        city_slug = normalize_slug(
            city
        )

        return (
            "https://mx.computrabajo.com/"
            f"empleos-en-{city_slug}"
        )

    return (
        "https://mx.computrabajo.com/"
        "empleos-en-mexico"
    )


def main():

    input_data = sys.stdin.read()

    if not input_data:

        print(
            "No se recibieron criterios",
            file=sys.stderr
        )

        sys.exit(1)

    criteria = json.loads(
        input_data
    )

    sources = criteria.get(
        "sources",
        []
    )

    all_jobs = []
    source_results = []

    # =====================================================
    # CONSULTAR FUENTES
    # =====================================================

    for source_name in sources:

        # -------------------------------------------------
        # JOOBLE
        # -------------------------------------------------

        if source_name == "jooble":

            try:

                print(
                    "[Jooble] "
                    "Iniciando búsqueda...",
                    file=sys.stderr
                )

                jobs = search_jooble(
                    criteria
                )

                all_jobs.extend(
                    jobs
                )

                source_results.append({
                    "source": "jooble",
                    "method": "api",
                    "access": "success",
                    "httpStatus": None,
                    "message": (
                        f"Se encontraron "
                        f"{len(jobs)} ofertas."
                    ),
                    "jobs": jobs
                })

            except Exception as error:

                print(
                    f"[Jooble] Error: {error}",
                    file=sys.stderr
                )

                source_results.append({
                    "source": "jooble",
                    "method": "api",
                    "access": "error",
                    "httpStatus": None,
                    "message": str(error),
                    "jobs": []
                })

        # -------------------------------------------------
        # ADZUNA
        # -------------------------------------------------

        elif source_name == "adzuna":

            try:

                print(
                    "[Adzuna] "
                    "Iniciando búsqueda...",
                    file=sys.stderr
                )

                jobs = search_adzuna(
                    criteria
                )

                all_jobs.extend(
                    jobs
                )

                source_results.append({
                    "source": "adzuna",
                    "method": "api",
                    "access": "success",
                    "httpStatus": 200,
                    "message": (
                        f"Se encontraron "
                        f"{len(jobs)} ofertas."
                    ),
                    "jobs": jobs
                })

            except Exception as error:

                print(
                    f"[Adzuna] Error: {error}",
                    file=sys.stderr
                )

                source_results.append({
                    "source": "adzuna",
                    "method": "api",
                    "access": "error",
                    "httpStatus": None,
                    "message": str(error),
                    "jobs": []
                })

        # -------------------------------------------------
        # COMPUTRABAJO
        # -------------------------------------------------

        elif source_name == "computrabajo":

            try:

                url = get_computrabajo_url(
                    criteria
                )

                print(
                    "[Computrabajo] "
                    f"Consultando: {url}",
                    file=sys.stderr
                )

                result = scrape_html_portal(
                    "computrabajo",
                    url,
                    criteria
                )

                source_results.append(
                    result
                )

                all_jobs.extend(
                    result["jobs"]
                )

                print(
                    "[Computrabajo] "
                    f"{result['access']} - "
                    f"{len(result['jobs'])} ofertas",
                    file=sys.stderr
                )

            except Exception as error:

                print(
                    "[Computrabajo] "
                    f"Error: {error}",
                    file=sys.stderr
                )

                source_results.append({
                    "source": "computrabajo",
                    "method": "html",
                    "access": "error",
                    "httpStatus": None,
                    "message": str(error),
                    "jobs": []
                })

    # =====================================================
    # FILTROS COMUNES
    # =====================================================

    total_before_filters = len(
        all_jobs
    )

 
    filtered_jobs = filter_jobs(
        all_jobs,
        criteria
    )

    print(
        "[Filtros] "
        f"Ofertas recibidas: {len(all_jobs)}",
        file=sys.stderr
    )

    print(
        "[Filtros] "
        f"Ofertas después de filtros: "
        f"{len(filtered_jobs)}",
        file=sys.stderr
    )



    # =====================================================
    # DEDUPLICACIÓN
    # =====================================================

    total_before_deduplication = len(
        filtered_jobs
    )

    unique_jobs = deduplicate_jobs(
        filtered_jobs
    )

    duplicates_removed = (
        total_before_deduplication
        - len(unique_jobs)
    )

    print(
        "[Deduplicación] "
        f"{total_before_deduplication} → "
        f"{len(unique_jobs)} ofertas "
        f"({duplicates_removed} duplicadas eliminadas)",
        file=sys.stderr
    )

    # =====================================================
    # RESULTADO FINAL
    # =====================================================

    result = {
        "criteria": criteria,
        "sources": source_results,
        "jobs": unique_jobs,
        "totalJobs": len(unique_jobs)
    }

    print(
        json.dumps(
            result,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()
