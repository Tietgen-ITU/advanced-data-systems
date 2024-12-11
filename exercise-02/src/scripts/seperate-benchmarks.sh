#!/bin/bash

declare -a benchmarks=("SSBQ1v1S100T4" "SSBQ1v1S100T1" "SSBQ1v1S100T8" "SSBQ1v1S1T4" "SSBQ1v1S10T4", "SSBQ2v2S100T4" "SSBQ2v2S100T1" "SSBQ2v2S100T8" "SSBQ2v2S1T4" "SSBQ2v2S10T4", "SSBQ4v1S100T4" "SSBQ4v1S100T1" "SSBQ4v1S100T8" "SSBQ4v1S1T4" "SSBQ4v1S10T4" )

mkdir -p ../results

for val in "${benchmarks[@]}"
do
	jq --arg name $val '.[] | select(.benchmark_name == $name)' ../duckdb/ssb-benchmark.log > "../results/ssb-benchmark-${val}.log"
done