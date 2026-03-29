CREATE TABLE IF NOT EXISTS raw_vacancies (
    id TEXT PRIMARY KEY,
    payload JSONB NOT NULL,
    loaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS staging_vacancies (
    id TEXT PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    salary_from INTEGER,
    salary_to INTEGER,
    currency TEXT,
    experience TEXT,
    employment_type TEXT,
    published_at TIMESTAMP,
    skills TEXT[],
    processed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vacancies_skill_stats (
    skill TEXT PRIMARY KEY,
    avg_salary INTEGER,
    vacancies_count INTEGER,
    calculated_at TIMESTAMP DEFAULT NOW()
);