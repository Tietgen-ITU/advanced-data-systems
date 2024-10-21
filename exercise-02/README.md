# Exercise 2

## Steps to build DuckDB

Navigate to `./duckdb` and execute the following command:

```bash
GEN=ninja BUILD_BENCHMARK=1 EXTENSION_CONFIGS="extension_config.cmake" make
```

### Notes about running benchmarks using the builtin `benchmark_runner`

When running benchmarks using the benchmark runner i noticed that we could not get as much statistics as I wanted. But i noticed a hidden flag in duckdb. For context, DuckDB has the possibility to output elapsed query times in a very poor format by using the `--out=<path and name of file to output>`. However, by looking at the code you will see that the `benchmark_runner` actually tries to output more details about the query in the json format. However, this is only being set if you use the `--log=<path and name of the file to output>`. 

The nice things about this is that we can decide what the output should be since we can override the `Benchmark::GetLogOutput` or so it seems like.

So what I am trying to do now is to build my benchmarks using the defined `duckdb_benchmark` macros located in `benchmark/include`. I am going to create my own macro to automatically build the different configurations of benchmarks that I need and then run them.
Maybe I will have to overwrite the `GetLogOutput` function, if it is possible.
