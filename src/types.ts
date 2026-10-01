
export interface SearchCriteria {
    country: string;
    state?: string;
    city?: string;
    position: string;
    modality?: string;
    salaryMin?: number;
    salaryMax?: number;
    radiusKm?: number;
    sources: string[];
}

export interface Job {
    source: string;
    id?: string;
    title: string;
    company: string | null;
    location: string | null;
    modality: string | null;
    salaryMin: number | null;
    salaryMax: number | null;
    salaryCurrency: string | null;
    salaryText?: string | null;
    description: string | null;
    url: string;
    publishedAt: string | null;
}

export type AccessStatus =
    | "success"
    | "blocked"
    | "unauthorized"
    | "rate_limited"
    | "not_found"
    | "timeout"
    | "server_error"
    | "connection_error"
    | "not_extractable"
    | "error";

export interface SourceResult {
    source: string;
    method: "api" | "html";
    access: AccessStatus;
    httpStatus: number | null;
    message: string;
    jobs: Job[];
    elapsedMs?: number;
}

export interface ScraperResult {
    criteria: SearchCriteria;
    sources: SourceResult[];
    jobs: Job[];
    totalJobs: number;
}

