.PHONY: plot build-benchmarks benchmark benchmark-clean seperate-benchmarks table plot-operators

plot:
	python3 plot.py ../duckdb/ssb-benchmark.log

plot-operators:
	python3 plot-operators.py ../duckdb/ssb-benchmark.log

table:
	python3 gen-data-table.py ../duckdb/ssb-benchmark.log

build-benchmarks:
	sh -c 'cd ../duckdb && GEN=ninja BUILD_BENCHMARK=1 EXTENSION_CONFIGS="extension_config.cmake" make'

benchmark:
	sh -c 'cd ../duckdb/build/release/benchmark && ./benchmark_runner --log=ssb-benchmark.log --out=ssb-elapsed.out --detailed-profile --disable-timeout "SSB.*"'
	mv ../duckdb/ssb-benchmark.log .
	mv ../duckdb/ssb-elapsed.out .

# benchmark-clean:
# 	sed ':a;N;$!ba;s/}\n{/},\n{/g' ssb-benchmark.log > ssb-benchmark-temp.log
# 	echo "[" > ssb-benchmark-fixed.log
#     cat ssb-benchmark-temp.log >> ssb-benchmark-fixed.log
#     echo "]" >> ssb-benchmark-fixed.log
#     rm ssb-benchmark-temp.log

seperate-benchmarks:
	sh ./scripts/seperate-benchmarks.sh

render-operator-tree:
	mkdir -p ../results/operator-trees
	sh ./scripts/render-operator-tree.sh "../results/*.log"
