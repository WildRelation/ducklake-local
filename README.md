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

**Linux / macOS:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 3 — Verify the connection

Run `main.py` once to confirm that DuckDB can connect to PostgreSQL and MinIO, and that DuckLake initializes correctly:

```bash
python main.py
```

You should see `Connected to local DuckLake.` and a list of tables (empty on the first run — that is expected).

`main.py` is not the application — it is a starting point. The `connect()` function inside it is what you reuse in your own scripts to get a connection to the lake. The commented-out code at the bottom is just a reference example of how to create tables and insert data; you do not need to uncomment it.

---

## CRUD operations

DuckLake supports full CRUD directly from Python — no API needed. Run the included example:

```bash
python crud.py
```

### Create

```python
con = connect()

con.execute("""
    CREATE TABLE IF NOT EXISTS my_lake.main.products (
        id    INT,
        name  VARCHAR,
        price DOUBLE,
        stock INT
    )
""")

con.execute("""
    INSERT INTO my_lake.main.products VALUES
        (1, 'Laptop',   9999.0, 15),
        (2, 'Mouse',     299.0, 50),
        (3, 'Keyboard', 1299.0, 30)
""")
```

### Read

```python
con.execute("SELECT * FROM my_lake.main.products").fetchdf()
```

### Update

```python
con.execute("""
    UPDATE my_lake.main.products
    SET price = 8999.0
    WHERE id = 1
""")
```

### Delete

```python
con.execute("""
    DELETE FROM my_lake.main.products
    WHERE id = 2
""")
```

> An API is only needed when you want to expose these operations to a web application or other users.

---

## Interactive SQL shell (optional)

Instead of writing Python, you can explore your DuckLake directly with the DuckDB UI in the browser.

**Linux / macOS:**
```bash
chmod +x shell.sh
./shell.sh
```

**Windows (PowerShell):**
```powershell
.\shell.ps1
```

This runs DuckDB inside a Docker container, connects to your local DuckLake automatically via `setup.sql`, and opens a web UI where you can run SQL queries interactively. Type `.exit` to close it.

---

## What we improved over a basic setup

| Change | Why |
|---|---|
| `docker-compose.yml` → `compose.yml` | `compose.yml` is the modern standard for Docker Compose v2. The old filename is a legacy convention from v1. |
| Health checks | Without them, the `mc` container tries to create the bucket before MinIO is ready and fails. Health checks make each service wait until the previous one is actually running. |
| Volumes | Without volumes, all data is lost when you run `docker compose down`. Volumes store data outside the container so it survives restarts. |
| Automatic bucket creation (`mc` container) | The bucket is created by Docker when the services start, not by the Python script. This means Python only needs to connect and query — no setup logic in the code. |
| `minio` removed from `requirements.txt` | The Python `minio` package was only needed to create the bucket. Since Docker handles that now, it is no longer a dependency. |

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
