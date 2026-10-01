

import re

from sources.web_scraper import fetch_page


def parse_salary(salary_text):
    if not salary_text:
        return None, None, None

    text = salary_text.strip()

    # Detectar moneda
    currency = "MXN" if "$" in text else None

    # Extraer cantidades como:
    # 30,000.00
    # 12,000
    # 10,833.50
    matches = re.findall(
        r"\$?\s*([\d,]+(?:\.\d+)?)",
        text
    )

    values = []

    for match in matches:
        try:
            value = float(
                match.replace(",", "")
            )
            values.append(value)
        except ValueError:
            continue

    if not values:
        return None, None, currency

    # Evitar interpretar números pequeños que puedan
    # aparecer fuera del salario.
    if len(values) == 1:
        return (
            values[0],
            values[0],
            currency
        )

    return (
        min(values),
        max(values),
        currency
    )


def scrape_html_portal(
    source_name,
    url,
    criteria
):
    result = fetch_page(url)

    if not result["success"]:
        return {
            "source": source_name,
            "method": "html",
            "access": result["access"],
            "httpStatus": result["httpStatus"],
            "message": result["message"],
            "jobs": [],
            "elapsedMs": result["elapsedMs"]
        }

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(
        result["html"],
        "html.parser"
    )

    if source_name == "computrabajo":
        jobs = extract_computrabajo_jobs(
            soup
        )
    else:
        jobs = extract_jobs(
            source_name,
            soup,
            criteria
        )

    if not jobs:
        return {
            "source": source_name,
            "method": "html",
            "access": "not_extractable",
            "httpStatus": result["httpStatus"],
            "message": (
                "El portal respondió correctamente, "
                "pero no se encontraron ofertas "
                "con el extractor configurado."
            ),
            "jobs": [],
            "elapsedMs": result["elapsedMs"]
        }

    return {
        "source": source_name,
        "method": "html",
        "access": "success",
        "httpStatus": result["httpStatus"],
        "message": (
            f"Se encontraron {len(jobs)} ofertas."
        ),
        "jobs": jobs,
        "elapsedMs": result["elapsedMs"]
    }


def extract_computrabajo_jobs(
    soup
):
    jobs = []

    cards = soup.select(
        "article.box_offer"
    )

    for card in cards:

        title_element = card.select_one(
            "h2 a.js-o-link"
        )

        if not title_element:
            continue

        title = title_element.get_text(
            " ",
            strip=True
        )

        relative_url = (
            title_element.get("href") or ""
        )

        if relative_url.startswith("/"):
            url = (
                "https://mx.computrabajo.com"
                + relative_url
            )
        else:
            url = relative_url

        # -------------------------------------------------
        # Empresa
        # -------------------------------------------------
        company_element = card.select_one(
            "[offer-grid-article-company-url]"
        )

        company = None

        if company_element:
            company_text = company_element.get_text(
                " ",
                strip=True
            )

            if company_text:
                company = company_text

        # -------------------------------------------------
        # Ubicación
        # -------------------------------------------------
        location = None

        location_elements = card.select(
            "p.fs16.fc_base.mt5 span"
        )

        for element in location_elements:

            text = element.get_text(
                " ",
                strip=True
            )

            if not text:
                continue

            try:
                value = float(text)

                if 0 <= value <= 5:
                    continue

            except ValueError:
                pass

            if any(
                char.isalpha()
                for char in text
            ):
                location = text
                break

        if location is None:

            possible_locations = card.select(
                "[class*='location'], "
                "[class*='ubicacion'], "
                "[class*='location'] span"
            )

            for element in possible_locations:

                text = element.get_text(
                    " ",
                    strip=True
                )

                if not text:
                    continue

                try:
                    value = float(text)

                    if 0 <= value <= 5:
                        continue

                except ValueError:
                    pass

                if any(
                    char.isalpha()
                    for char in text
                ):
                    location = text
                    break

        # -------------------------------------------------
        # Salario
        # -------------------------------------------------
        salary_element = card.select_one(
            ".i_salary"
        )

        salary = None
        salary_min = None
        salary_max = None
        salary_currency = None

        if salary_element:

            salary_container = (
                salary_element.parent
            )

            salary_text = salary_container.get_text(
                " ",
                strip=True
            )

            if salary_text:
                salary = salary_text

                (
                    salary_min,
                    salary_max,
                    salary_currency
                ) = parse_salary(
                    salary_text
                )

        # -------------------------------------------------
        # ID
        # -------------------------------------------------
        job_id = card.get(
            "data-id"
        )

        jobs.append({
            "source": "computrabajo",
            "id": job_id,
            "title": title,
            "company": company,
            "location": location,
            "modality": None,
            "salaryMin": salary_min,
            "salaryMax": salary_max,
            "salaryCurrency": salary_currency,
            "description": None,
            "url": url,
            "publishedAt": None,
            "salaryText": salary
        })

    return jobs


def extract_jobs(
    source_name,
    soup,
    criteria
):
    jobs = []

    cards = soup.select(
        "article"
    )

    for card in cards:

        title_element = card.select_one(
            "h2, h3"
        )

        if not title_element:
            continue

        title = title_element.get_text(
            " ",
            strip=True
        )

        jobs.append({
            "source": source_name,
            "id": None,
            "title": title,
            "company": None,
            "location": None,
            "modality": None,
            "salaryMin": None,
            "salaryMax": None,
            "salaryCurrency": None,
            "description": None,
            "url": "",
            "publishedAt": None
        })

    return jobs
