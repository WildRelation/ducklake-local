#!/usr/bin/env bash
docker run --rm -it \
    -v $(pwd):/workspace \
    -w /workspace \
    --net host \
    --entrypoint /duckdb \
    duckdb/duckdb -init setup.sql -ui
