# Weather API Pipeline Project

This repository contains a weather-data pipeline that uses Apache Airflow, PostgreSQL, and dbt. Everything runs via Docker Compose so you can bring the full stack up quickly for demos or local development.

## Architecture Overview
- `postgres_container`: PostgreSQL database (schema `dev`) that stores both raw data and modeled tables.
- `airflow_container`: Apache Airflow 3 image with an API helper script `api/insert_records.py` for fetching WeatherStack data (or mock data) and loading it into PostgreSQL.
- `dbt_container`: Executes the dbt project located in `dbt/my_project`, producing staging and mart tables in the `dev` schema.
- Volumes: `postgres_data` persists database data. Project directories are mounted so you can edit code from the host.

## Prerequisites
- Docker & Docker Compose v2
- Network access for WeatherStack API calls (script falls back to mock data if the API rate-limits you)
- WeatherStack API key (recommended) – the repo ships with a sample key; replace it with your own.

## Environment Setup
```bash
cd api_request
```
Update the API key in `airflow/api/api_request.py`:
```python
api_key = "<YOUR_WEATHERSTACK_API_KEY>"
```

## Run The Pipeline
1. **Start PostgreSQL**
   ```bash
   docker compose up -d db
   ```
2. **Load raw data into the database**
   ```bash
   docker compose run --rm af python /opt/airflow/api/insert_records.py
   ```
   The script will:
   - Connect to PostgreSQL as `db_user`/`db_password`
   - Create schema `dev` and table `raw_weather_data` if they are missing
   - Call the WeatherStack API; on failure (e.g., HTTP 429) it automatically falls back to mock data
   - Insert a sample record into the table
3. **Run dbt models**
   ```bash
   docker compose up dbt
   ```
   dbt builds three tables: `dev.stg_weather_report`, `dev.daily_average`, and `dev.weather_report`.
4. **Inspect results**
   ```bash
   docker compose exec db psql -U db_user -d db -c "\dt dev.*"
   docker compose exec db psql -U db_user -d db -c "SELECT * FROM dev.weather_report;"
   ```

## Repository Layout
```
api_request/
├── airflow/
│   ├── api/
│   │   ├── api_request.py      # WeatherStack API client + mock data
│   │   └── insert_records.py   # creates table & inserts data
│   └── dags/                   # placeholder for Airflow DAGs
├── dbt/
│   └── my_project/
│       ├── models/
│       │   ├── staging/stg_weather_report.sql
│       │   ├── marts/daily_average.sql
│       │   └── marts/weather_report.sql
│       ├── models/sources/sources.yml
│       └── profiles (mounted at runtime)
├── docker-compose.yml
└── postgres/
    └── airflow_init.sql        # seeds Airflow DB/user
```

## Useful Commands
- Stop the entire stack: `docker compose down`
- Reset PostgreSQL data:
  ```bash
  docker compose down -v
  # or remove the legacy bind-mounted directory if any:
  sudo rm -rf api_request/postgres_data
  ```
- Tail logs:
  ```bash
  docker compose logs db
  docker compose logs af
  docker compose logs dbt
  ```

## Troubleshooting
- **`initdb: directory "/var/lib/postgresql/data" exists but is not empty`**: remove the old volume (`docker compose down -v`) before restarting.
- **dbt error `relation "dev.raw_weather_data" does not exist`**: make sure you ran `insert_records.py` (step 2) to create/populate the source table.
- **WeatherStack HTTP 429 rate limit**: the script automatically switches to mock data; for real-time data consider upgrading your API plan or adding retries.

## Next Steps
- Build an Airflow DAG that orchestrates the ingestion and dbt run on a schedule.
- Add dbt tests or additional validation to monitor data quality.
- Move the API key into an environment variable or secrets manager for better security.
