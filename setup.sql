INSTALL ducklake;
INSTALL postgres;

LOAD ducklake;
LOAD postgres;

CREATE OR REPLACE SECRET minio_secret (
    TYPE s3,
    KEY_ID 'minioadmin',
    SECRET '87654321',
    ENDPOINT '127.0.0.1:9000',
    URL_STYLE 'path',
    USE_SSL false
);

ATTACH 'ducklake:postgres:host=127.0.0.1 dbname=ducklake user=duck password=123456 port=5432'
AS my_lake (DATA_PATH 's3://ducklake/');

USE my_lake;
