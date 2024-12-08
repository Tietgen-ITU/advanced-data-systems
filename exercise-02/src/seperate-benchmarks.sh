#!/bin/bash
QUERIES=("SSBQ1v1S100T4" "SSBQ2v2S100T4" "SSBQ4v1S100T4")

for val in ${QUERIES[@]} 
do 
    jq --arg BENCH "${val}" '.[] | select(.benchmark_name == $BENCH)' ../duckdb/ssb-benchmark-fixed.log > "ssb-benchmark-${val}.log"
done