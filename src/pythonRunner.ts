
import { spawn } from "child_process";
import path from "path";
import {
    SearchCriteria,
    ScraperResult
} from "./types";

export function runPythonScraper(
    criteria: SearchCriteria
): Promise<ScraperResult> {

    return new Promise((resolve, reject) => {

        const pythonCommand =
            process.env.PYTHON_COMMAND || "python";

        const scriptPath = path.join(
            process.cwd(),
            "src",
            "python",
            "scraper.py"
        );

        const python = spawn(
            pythonCommand,
            [scriptPath]
        );

        let output = "";
        let errorOutput = "";

        python.stdin.write(
            JSON.stringify(criteria)
        );

        python.stdin.end();

        python.stdout.on(
            "data",
            (data: Buffer) => {
                output += data.toString();
            }
        );

        python.stderr.on(
            "data",
            (data: Buffer) => {
                errorOutput += data.toString();
            }
        );

        python.on(
            "error",
            (error) => {
                reject(error);
            }
        );

        python.on(
            "close",
            (code) => {

                if (code !== 0) {
                    reject(
                        new Error(
                            `Python terminó con código ${code}: ${errorOutput}`
                        )
                    );

                    return;
                }

                try {

                    const result: ScraperResult =
                        JSON.parse(output);

                    resolve(result);

                } catch {

                    reject(
                        new Error(
                            "Python devolvió una respuesta JSON inválida."
                        )
                    );
                }
            }
        );
    });
}
