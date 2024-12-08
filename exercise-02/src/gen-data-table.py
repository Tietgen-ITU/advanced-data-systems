from itertools import groupby
import sys
from models.models import *

def output_rows_scanned(measurements):
    print("Average rows scanned for each query")
    print("===================================")

    scale_factors = get_scale_factors(measurements)

    for sf in scale_factors:
        print(f"Scale factor: {sf}")

        for m in thread1_measeurements:
            if m.scale_factor == sf:
                print(f"Query {m.query_name}: {m.average_by_rows_scanned()}")

    print()

def output_rows_cardinality(measurements):
    print("Average rows cardinality for each query")
    print("=======================================")

    scale_factors = get_scale_factors(measurements)

    for sf in scale_factors:
        print(f"Scale factor: {sf}")

        for m in thread1_measeurements:
            if m.scale_factor == sf:
                print(f"Query {m.query_name}: {m.average_by_rows_cardinality()}")

    print()

def output_rows_scanned_sf(measurements):
    print("Average rows scanned for each query")
    print("===================================")

    threads = get_thread_counts(measurements)

    for t in threads:
        print(f"Thread count: {t}")

        for m in measurements:
            if m.thread_count == t:
                print(f"Query {m.query_name}: {m.average_by_rows_scanned()}")

    print()

def output_rows_cardinality_sf(measurements):
    print("Average rows cardinality for each query")
    print("=======================================")

    threads = get_thread_counts(measurements)

    for t in threads:
        print(f"Thread count: {t}")

        for m in measurements:
            if m.thread_count == t:
                print(f"Query {m.query_name}: {m.average_by_rows_cardinality()}")
    
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python plot.py <bench file path>")
        exit(1)

    measurements = read_data(sys.argv[1])
    groups = [MeasurementGroup(key=k, measurements=list(g)) for k, g in groupby(
        sorted(measurements, key=lambda x: x.get_name()), lambda x: x.get_name())]
    groups.sort(key=lambda x: x.key)

    queries = set([ "1.1", "2.2", "4.1" ])

    thread1_measeurements = [m for m in groups if m.thread_count == 4 and m.query_name in queries]
    scale100_measeurements = [m for m in groups if m.scale_factor == 100 and m.query_name in queries]

    output_rows_scanned(thread1_measeurements)
    output_rows_scanned_sf(scale100_measeurements)

    output_rows_cardinality(thread1_measeurements)
    output_rows_cardinality_sf(scale100_measeurements)
