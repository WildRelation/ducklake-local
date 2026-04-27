# DuckLake Local Development Setup

Local environment for developing and testing against a DuckLake instance before deploying to production (cbhcloud).

## How it works

```
DuckLake = PostgreSQL (catalog) + MinIO (parquet files)
```

Both services run locally via Docker. DuckDB connects to them from Python. The bucket in MinIO is created automatically when the containers start.

| Component | Local | Production (cbhcloud) |
|---|---|---|
| PostgreSQL | `localhost:5432` | SSH tunnel → cbhcloud |
| MinIO | `localhost:9000` | `ducklake-minio.app.cloud.cbh.kth.se` |
| SSL | No | Yes |

---

## Prerequisites

- Python 3.10+
- Docker + Docker Compose:
  - **Windows / macOS** — install [Docker Desktop](https://www.docker.com/products/docker-desktop/), Docker Compose is included
  - **Linux** — install Docker Engine and then the Compose plugin separately:
    ```bash
    sudo apt install docker-compose-plugin   # Debian/Ubuntu
    ```
    Verify it works with `docker compose version`

---

## Step 1 — Start the services

```bash
docker compose up -d
```

This starts PostgreSQL and MinIO in the background and automatically creates the `ducklake` bucket. To stop them:

```bash
docker compose down
```

Your data is safe — it is stored in Docker volumes and survives restarts.

You can access the **MinIO web console** at `http://localhost:9001`
Login: `minioadmin` / `87654321`

---

## Step 2 — Set up the Python environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 3 — Run the script

```bash
python main.py
```

On the first run DuckLake initializes the catalog in PostgreSQL. After that you are ready to create tables and insert data.

---

## Creating tables and inserting data

```python
con = connect()

con.execute("""
    CREATE TABLE IF NOT EXISTS my_lake.main.users (
        id    INT,
        name  VARCHAR,
        email VARCHAR
    );
""")

con.execute("""
    INSERT INTO my_lake.main.users VALUES
        (1, 'Alice', 'alice@example.com'),
        (2, 'Bob',   'bob@example.com');
""")

print(con.execute("SELECT * FROM my_lake.main.users").fetchdf())
```

---

## Difference from production

| | Local | Production |
|---|---|---|
| PostgreSQL host | `localhost` | `localhost` via SSH tunnel |
| MinIO endpoint | `localhost:9000` | `ducklake-minio.app.cloud.cbh.kth.se` |
| MinIO SSL | `false` | `true` |
| SSH tunnel needed | No | Yes |
| Bucket creation | Automatic (Docker) | Automatic (Docker) |

The only changes needed to switch from local to production are the credentials and endpoints at the top of `main.py`.
