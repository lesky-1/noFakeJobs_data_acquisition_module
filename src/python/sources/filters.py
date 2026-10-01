
import re
import unicodedata


def normalize_text(value):
    """
    Normaliza texto para poder compararlo.
    """

    if not value:
        return ""

    value = str(value).strip().lower()

    value = unicodedata.normalize(
        "NFD",
        value
    )

    value = "".join(
        char
        for char in value
        if unicodedata.category(char) != "Mn"
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value


def normalize_url(url):
    """
    Normaliza una URL para detectar duplicados.
    """

    if not url:
        return ""

    url = url.strip().lower()

    # Eliminamos slash final
    url = url.rstrip("/")

    return url


def filter_jobs(jobs, criteria):
    """
    Aplica los filtros comunes a todas las fuentes.

    IMPORTANTE:
    La ausencia de salario NO elimina una oferta.
    Las ofertas sin salario declarado se conservan
    para que posteriormente puedan ser evaluadas
    por el modelo de detección de ofertas falsas.
    """

    position = normalize_text(
        criteria.get("position")
    )

    city = normalize_text(
        criteria.get("city")
    )

    modality = normalize_text(
        criteria.get("modality")
    )

    salary_min = criteria.get(
        "salaryMin"
    )

    salary_max = criteria.get(
        "salaryMax"
    )

    filtered = []

    for job in jobs:

        # -------------------------------------------------
        # 1. Puesto
        # -------------------------------------------------

        if position:

            title = normalize_text(
                job.get("title")
            )

            description = normalize_text(
                job.get("description")
            )

            searchable_text = (
                f"{title} {description}"
            )

            if position not in searchable_text:
                continue

        # -------------------------------------------------
        # 2. Ciudad
        # -------------------------------------------------

        if city:

            location = normalize_text(
                job.get("location")
            )

            if city not in location:
                continue

        # -------------------------------------------------
        # 3. Modalidad
        # -------------------------------------------------

        if modality:

            job_modality = normalize_text(
                job.get("modality")
            )

            # También buscamos la modalidad en título
            # y descripción porque algunos portales
            # no tienen un campo estructurado.
            title = normalize_text(
                job.get("title")
            )

            description = normalize_text(
                job.get("description")
            )

            modality_text = (
                f"{job_modality} "
                f"{title} "
                f"{description}"
            )

            if modality not in modality_text:
                continue

        # -------------------------------------------------
        # 4. Sueldo mínimo
        # -------------------------------------------------

        if salary_min:

            job_salary_min = job.get(
                "salaryMin"
            )

            job_salary_max = job.get(
                "salaryMax"
            )

            # ---------------------------------------------
            # SIN SALARIO:
            #
            # NO descartamos la oferta.
            # ---------------------------------------------

            if (
                job_salary_min is None
                and job_salary_max is None
            ):
                filtered.append(job)
                continue

            comparable_salary = (
                job_salary_max
                if job_salary_max is not None
                else job_salary_min
            )

            if comparable_salary < salary_min:
                continue

        # -------------------------------------------------
        # 5. Sueldo máximo
        # -------------------------------------------------

        if salary_max:

            job_salary_min = job.get(
                "salaryMin"
            )

            # Sin salario declarado:
            # conservamos la oferta.
            if job_salary_min is None:
                filtered.append(job)
                continue

            if job_salary_min > salary_max:
                continue

        filtered.append(job)

    return filtered


def deduplicate_jobs(jobs):
    """
    Elimina ofertas duplicadas entre portales.

    Estrategia:

    1. URL normalizada, si existe.
    2. Puesto + empresa + ubicación.

    No usamos solamente el título porque diferentes
    empresas pueden publicar puestos con el mismo nombre.
    """

    unique_jobs = []

    seen_urls = set()
    seen_fingerprints = set()

    for job in jobs:

        # -------------------------------------------------
        # 1. Duplicado por URL
        # -------------------------------------------------

        url = normalize_url(
            job.get("url")
        )

        if url:

            if url in seen_urls:
                continue

            seen_urls.add(url)

        # -------------------------------------------------
        # 2. Duplicado por puesto + empresa + ubicación
        # -------------------------------------------------

        title = normalize_text(
            job.get("title")
        )

        company = normalize_text(
            job.get("company")
        )

        location = normalize_text(
            job.get("location")
        )

        # Solo hacemos fingerprint si tenemos
        # información suficiente.
        if title and company and location:

            fingerprint = (
                f"{title}|"
                f"{company}|"
                f"{location}"
            )

            if fingerprint in seen_fingerprints:

                # Si ya fue detectado por fingerprint,
                # eliminamos este duplicado.
                continue

            seen_fingerprints.add(
                fingerprint
            )

        unique_jobs.append(job)

    return unique_jobs
