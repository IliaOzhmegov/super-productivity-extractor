-- V1__Initial_setup.sql
CREATE SCHEMA IF NOT EXISTS time_tracking;

CREATE TABLE time_tracking.projects (
    project_id VARCHAR PRIMARY KEY,
    project_title VARCHAR(255) NOT NULL
);

CREATE TABLE time_tracking.tasks (
    task_id VARCHAR PRIMARY KEY,
    project_id VARCHAR NOT NULL,
    task_title VARCHAR(255) NOT NULL,
    FOREIGN KEY (project_id) REFERENCES time_tracking.projects (project_id)
);

CREATE TABLE time_tracking.time_spent (
    task_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    time_spent_ms INT NOT NULL,
    PRIMARY KEY (task_id, date),
    FOREIGN KEY (task_id) REFERENCES time_tracking.tasks (task_id)
);

-- Ingestion functions
CREATE OR REPLACE FUNCTION time_tracking.ingest_project(p_project_id VARCHAR, p_project_title VARCHAR)
RETURNS VOID AS $$
BEGIN
    INSERT INTO time_tracking.projects (project_id, project_title)
    VALUES (p_project_id, p_project_title)
    ON CONFLICT (project_id) DO UPDATE
    SET project_title = EXCLUDED.project_title;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION time_tracking.ingest_task(p_task_id VARCHAR, p_project_id VARCHAR, p_task_title VARCHAR)
RETURNS VOID AS $$
BEGIN
    INSERT INTO time_tracking.tasks (task_id, project_id, task_title)
    VALUES (p_task_id, p_project_id, p_task_title)
    ON CONFLICT (task_id) DO UPDATE
    SET task_title = EXCLUDED.task_title;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION time_tracking.ingest_time_spent(p_task_id VARCHAR, p_date DATE, p_time_spent_ms INTEGER)
RETURNS VOID AS $$
BEGIN
    INSERT INTO time_tracking.time_spent (task_id, date, time_spent_ms)
    VALUES (p_task_id, p_date, p_time_spent_ms)
    ON CONFLICT (task_id, date) DO UPDATE
    SET time_spent_ms = EXCLUDED.time_spent_ms;
END;
$$ LANGUAGE plpgsql;
