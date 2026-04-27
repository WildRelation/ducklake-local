import duckdb
from minio import Minio

# ── MinIO (local Docker) ─────────────────────────────────────────────────────
MINIO_ENDPOINT = "localhost:9000"
MINIO_USER     = "minioadmin"
MINIO_PASSWORD = "87654321"
BUCKET_NAME    = "ducklake"

# ── PostgreSQL (local Docker) ────────────────────────────────────────────────
PG_HOST     = "localhost"
PG_DB       = "ducklake"
PG_USER     = "duck"
PG_PASSWORD = "123456"
PG_PORT     = 5432


def ensure_bucket():
    """Creates the MinIO bucket if it does not exist."""
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_USER, secret_key=MINIO_PASSWORD, secure=False)
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)
        print(f"Bucket '{BUCKET_NAME}' created.")


def connect():
    """Returns a DuckDB connection with the DuckLake catalog attached."""
    con = duckdb.connect()

    con.execute("INSTALL ducklake;")
    con.execute("INSTALL postgres;")
    con.execute("LOAD ducklake;")
    con.execute("LOAD postgres;")

    con.execute(f"""
    CREATE OR REPLACE SECRET minio_secret (
        TYPE s3,
        KEY_ID '{MINIO_USER}',
        SECRET '{MINIO_PASSWORD}',
        ENDPOINT '{MINIO_ENDPOINT}',
        URL_STYLE 'path',
        USE_SSL false
    );
    """)

    con.execute(f"""
    ATTACH 'ducklake:postgres:host={PG_HOST} dbname={PG_DB} user={PG_USER} password={PG_PASSWORD} port={PG_PORT}'
    AS my_lake (DATA_PATH 's3://{BUCKET_NAME}/');
    """)

    return con


def main():
    ensure_bucket()
    con = connect()
    print("Connected to local DuckLake.\n")

    tables = con.execute("""
        SELECT database, schema, name
        FROM (SHOW ALL TABLES)
        WHERE database = 'my_lake'
    """).fetchall()

    print("Tables in my_lake:")
    if tables:
        for db, schema, name in tables:
            print(f"  {db}.{schema}.{name}")
    else:
        print("  (empty — no tables yet)")

    # ── Example: create a table and insert data ──────────────────────────────
    # Uncomment to try it out:

    # con.execute("CREATE TABLE IF NOT EXISTS my_lake.main.test (id INT, name VARCHAR);")
    # con.execute("INSERT INTO my_lake.main.test VALUES (1, 'Alice'), (2, 'Bob');")
    # print(con.execute("SELECT * FROM my_lake.main.test").fetchdf())


if __name__ == "__main__":
    main()
