# Exercise 2

## Steps to build DuckDB

Navigate to `./duckdb` and execute the following command:

> [!NOTE]
> At the moment I have not implemented my own extension. When that is done, it will be added to the list of extensions to be added in this project.

```bash
CORE_EXTENSIONS='autocomplete;tpch' GEN=ninja make
```
