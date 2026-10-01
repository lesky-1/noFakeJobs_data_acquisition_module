
import { runPythonScraper } from "./pythonRunner";
import { SearchCriteria } from "./types";

async function main() {

    // =====================================================
    // CONFIGURACIÓN DE LA BÚSQUEDA
    // =====================================================

    const criteria: SearchCriteria = {

        country: "MX",

        state: "Jalisco",

        city: "Guadalajara",

        // Vacío = cualquier puesto
        position: "",

        // Vacío = cualquier modalidad
        modality: "",

        // 0 = sin filtro de salario mínimo
        salaryMin: 0,

        // undefined = sin filtro de salario máximo
        salaryMax: undefined,

        // 0 = sin filtro de radio
        radiusKm: 0,

        sources: [
            "jooble",
            "adzuna",
            "computrabajo"
        ]
    };

    // =====================================================
    // INFORMACIÓN DE LA BÚSQUEDA
    // =====================================================

    console.log("=================================");
    console.log("       JOB SCRAPER MX");
    console.log("=================================");

    console.log(
        `Puesto: ${
            criteria.position || "Cualquier puesto"
        }`
    );

    console.log(
        `Ubicación: ${
            criteria.city || "Cualquier ciudad"
        }, ${
            criteria.state || "Cualquier estado"
        }`
    );

    console.log(
        `Modalidad: ${
            criteria.modality || "Cualquiera"
        }`
    );

    console.log(
        `Sueldo mínimo: $${
            criteria.salaryMin ?? 0
        }`
    );

    console.log(
        `Sueldo máximo: ${
            criteria.salaryMax !== undefined
                ? `$${criteria.salaryMax}`
                : "Sin límite"
        }`
    );

    console.log(
        `Fuentes: ${criteria.sources.join(", ")}`
    );

    console.log("---------------------------------");

    try {

        const result =
            await runPythonScraper(criteria);

        // =================================================
        // ESTADO DE LAS FUENTES
        // =================================================

        console.log("");
        console.log("ESTADO DE LAS FUENTES");
        console.log("=================================");

        for (const source of result.sources) {

            console.log(
                `[${source.source}]`
            );

            console.log(
                `  Método: ${source.method}`
            );

            console.log(
                `  Acceso: ${source.access}`
            );

            console.log(
                `  HTTP: ${source.httpStatus ?? "N/A"}`
            );

            console.log(
                `  Mensaje: ${source.message}`
            );

            console.log(
                `  Ofertas: ${source.jobs.length}`
            );

            if (source.elapsedMs !== undefined) {

                console.log(
                    `  Tiempo: ${source.elapsedMs} ms`
                );
            }

            console.log("");
        }

        // =================================================
        // RESULTADO FINAL
        // =================================================

        console.log("=================================");
        console.log(
            `TOTAL DE OFERTAS: ${result.totalJobs}`
        );
        console.log("=================================");

        for (const job of result.jobs) {

            console.log("---------------------------------");

            console.log(
                `Portal: ${job.source}`
            );

            console.log(
                `Puesto: ${job.title}`
            );

            console.log(
                `Empresa: ${
                    job.company ??
                    "No especificada"
                }`
            );

            console.log(
                `Ubicación: ${
                    job.location ??
                    "No especificada"
                }`
            );

            // ---------------------------------------------
            // Mostrar salario
            // ---------------------------------------------

            if (job.salaryText) {

                console.log(
                    `Sueldo: ${job.salaryText}`
                );

            } else if (
                job.salaryMin !== null ||
                job.salaryMax !== null
            ) {

                const min =
                    job.salaryMin !== null
                        ? `$${job.salaryMin}`
                        : "";

                const max =
                    job.salaryMax !== null
                        ? `$${job.salaryMax}`
                        : "";

                console.log(
                    `Sueldo: ${min}${
                        min && max
                            ? " - "
                            : ""
                    }${max}`
                );

            } else {

                console.log(
                    "Sueldo: No especificado"
                );
            }

            console.log(
                `URL: ${job.url}`
            );
        }

    } catch (error) {

        console.error(
            "Error ejecutando el scraper:"
        );

        if (error instanceof Error) {

            console.error(
                error.message
            );

        } else {

            console.error(error);
        }

        process.exitCode = 1;
    }
}

main();

