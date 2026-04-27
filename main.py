import duckdb

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

    # con.execute("""
    #     CREATE TABLE IF NOT EXISTS my_lake.main.users (
    #         id    INT,
    #         name  VARCHAR,
    #         email VARCHAR
    #     );
    # """)
    # con.execute("""
    #     INSERT INTO my_lake.main.users VALUES
    #         (1, 'Alice', 'alice@example.com'),
    #         (2, 'Bob',   'bob@example.com');
    # """)
    # print(con.execute("SELECT * FROM my_lake.main.users").fetchdf())


if __name__ == "__main__":
    main()
