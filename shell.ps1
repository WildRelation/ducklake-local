docker run --rm -it `
    -v ${PWD}:/workspace `
    -w /workspace `
    --net host `
    --entrypoint /duckdb `
    duckdb/duckdb -init setup.sql -ui
