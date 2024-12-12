from collections import defaultdict
from itertools import groupby
import json
import pathlib
import sys
from typing import Any
import matplotlib.pyplot as plt
from dataclasses import dataclass
from models.models import MeasurementGroup, get_queries, get_thread_counts, get_scale_factors, read_data

from matplotlib.ticker import LogLocator, ScalarFormatter
import numpy as np

CURRENT_WORKING_DIRECTORY = pathlib.Path(__file__).parent.resolve()

markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x']
line_styles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--', '-.', ':', '-']
hatch_patterns = ['///', '\\\\', '...', '/', '\\', '-', 'O' ]


def get_plot_path(plot_name: str, group_name: str, format: str):
    if not (CURRENT_WORKING_DIRECTORY / "output").exists():
        (CURRENT_WORKING_DIRECTORY / "output").mkdir()
    if not (CURRENT_WORKING_DIRECTORY / "output" / format).exists():
        (CURRENT_WORKING_DIRECTORY / "output" / format).mkdir()
    if not (CURRENT_WORKING_DIRECTORY / "output" / format / group_name).exists():
        (CURRENT_WORKING_DIRECTORY / "output" / format / group_name).mkdir()

    out_path = CURRENT_WORKING_DIRECTORY / "output" / format / group_name / f"{plot_name}.{format}"
    return out_path

def plot_elapsed(groups: list[MeasurementGroup], name: str = "elapsed_line"):
    y_max = max(group.max_elapsed_time for group in groups)
    y_min = min(group.min_elapsed_time for group in groups)

    for query_name in get_queries(groups):
        plt.figure()
        ax = plt.gca()
        plt.ylim(y_min*0.9, y_max*1.1)

        for i, t in enumerate(get_thread_counts(groups)):
            gs = [group for group in groups if group.query_name == query_name and group.thread_count == t]
            gs.sort(key=lambda x: x.scale_factor)

            xs = [group.scale_factor for group in gs]
            ys = [group.average_by("elapsed_time") for group in gs]

            marker = markers[i]
            plt.loglog(xs, ys, f'-{marker}',
                       markerfacecolor=None, label=f"{t} threads")

        plt.title(f"Query {query_name} elapsed time")

        plt.legend()
        plt.ylabel("Query Elapsed Time (s)")
        plt.xlabel("Scale Factor")

        format = "pdf"
        out_path = get_plot_path(f"elapsed-q{query_name}", name, format)
        plt.savefig(out_path,
                format=format, bbox_inches="tight")

def plot_sf_elapsed(groups: list[MeasurementGroup], name: str = "elapsed_line"):
    y_max = max(group.max_elapsed_time for group in groups)
    y_min = min(group.min_elapsed_time for group in groups)

    plt.figure()
    ax = plt.gca()
    plt.ylim(y_min*0.9, y_max*1.1)

    for i, q in enumerate(get_queries(groups)):
        gs = [group for group in groups if group.query_name == q]
        gs.sort(key=lambda x: x.scale_factor)

        xs = [group.scale_factor for group in gs]
        ys = [group.average_by("elapsed_time") for group in gs]

        marker = markers[i]
        plt.loglog(xs, ys, f'-{marker}',
                    markerfacecolor=None, label=f"Query {q}")

    plt.title(f"Query elapsed time(Threads={4})")

    plt.legend()
    plt.ylabel("Query Elapsed Time (s)")
    plt.xlabel("Scale Factor")

    format = "pdf"
    out_path = get_plot_path(f"elapsed-t{4}", name, format)
    plt.savefig(out_path,
            format=format, bbox_inches="tight")

def plot_sf_rows(groups: list[MeasurementGroup], name: str = "elapsed_line"):
    y_max = max(group.average_by_rows_scanned() for group in groups)
    y_min = 20000000

    plt.figure()
    ax = plt.gca()
    plt.ylim(y_min*0.9, y_max*1.1)

    for i, q in enumerate(get_queries(groups)):
        gs = [group for group in groups if group.query_name == q]
        gs.sort(key=lambda x: x.scale_factor)

        xs = [group.scale_factor for group in gs]
        ys = [group.average_by_rows_scanned() for group in gs]
        print(ys)

        marker = markers[i]
        plt.loglog(xs, ys, f'-{marker}',
                    markerfacecolor=None, label=f"Query {q}")

    plt.title(f"Query rows scanned(Threads={4})")

    plt.legend()
    plt.ylabel("Rows scanned")
    plt.xlabel("Scale Factor")

    format = "pdf"
    out_path = get_plot_path(f"rows-threads-t{4}", name, format)
    plt.savefig(out_path,
            format=format, bbox_inches="tight")

def plot_thread_elapsed(groups: list[MeasurementGroup], name: str = "elapsed_thread_line"):
    y_max = max(group.max_elapsed_time for group in groups)
    y_min = min(group.min_elapsed_time for group in groups)

    for i, t in enumerate(get_thread_counts(groups)):
        plt.figure()
        ax = plt.gca()
        plt.ylim(y_min*0.95, y_max*1.05)

        for q_idx, query_name in enumerate(get_queries(groups)):
            gs = [group for group in groups if group.query_name == query_name and group.thread_count == t]
            gs.sort(key=lambda x: x.scale_factor)

            xs = [group.scale_factor for group in gs]
            ys = [group.average_by("elapsed_time") for group in gs]

            marker = markers[q_idx]
            line = line_styles[q_idx]
            plt.plot(xs, ys, 
                    marker=marker, 
                    linestyle=line,
                    markerfacecolor=None, 
                    label=f"Query {query_name}")

            plt.title(f"Query elapsed time using {t} threads")

        plt.legend()
        plt.ylabel("Query Elapsed Time (s)")
        plt.xlabel("Scale Factor")

        format = "pdf"
        out_path = get_plot_path(f"elapsed-t{t}", name, format)
        plt.savefig(out_path,
                format=format, bbox_inches="tight")

def plot_thread_scale_elapsed(groups: list[MeasurementGroup], name: str = "elapsed_thread_line"):
    y_max = max(group.max_elapsed_time for group in groups)
    y_min = min(group.min_elapsed_time for group in groups)

    plt.figure()
    plt.ylim(y_min*0.95, y_max*1.05)

    for q_idx, query_name in enumerate(get_queries(groups)):
        gs = [group for group in groups if group.query_name == query_name]
        gs.sort(key=lambda x: x.scale_factor)

        xs = [group.thread_count for group in gs]
        ys = [group.average_by("elapsed_time") for group in gs]

        marker = markers[q_idx]
        line = line_styles[q_idx]
        plt.loglog(xs, ys, 
                marker=marker, 
                linestyle=line,
                markerfacecolor=None, 
                label=f"Query {query_name}")

        plt.title(f"Query elapsed time(SF=100)")

        plt.legend()
        plt.ylabel("Query Elapsed Time (s)")
        plt.xlabel("Threads")

        format = "pdf"
        out_path = get_plot_path(f"elapsed-threads-sf100", name, format)
        plt.savefig(out_path,
                format=format, bbox_inches="tight")

def plot_thread_scale_rows(groups: list[MeasurementGroup], name: str = "elapsed_thread_line"):
    y_max = max(group.average_by_rows_scanned() for group in groups)
    y_min = 20000000

    plt.figure()
    ax = plt.gca()
    plt.ylim(y_min*0.9, y_max*1.1)

    for i, q in enumerate(get_queries(groups)):
        gs = [group for group in groups if group.query_name == q]
        gs.sort(key=lambda x: x.scale_factor)

        xs = [group.thread_count for group in gs]
        ys = [group.average_by_rows_scanned() for group in gs]
        print(ys)

        marker = markers[i]
        plt.plot(xs, ys, f'-{marker}',
                    markerfacecolor=None, label=f"Query {q}")

    plt.title(f"Query rows scanned(SF={100})")

    plt.legend()
    plt.ylabel("Rows scanned")
    plt.xlabel("Threads")

    format = "pdf"
    out_path = get_plot_path(f"rows-scalefacor-100", name, format)
    plt.savefig(out_path,
            format=format, bbox_inches="tight")

def plot_scale_bar_elapsed(groups: list[MeasurementGroup], name: str = "elapsed_bar"):
    y_max = max(group.average_by("elapsed_time")*1000 for group in groups if group.thread_count == 4)
    y_min = min(group.min_elapsed_time*1000 for group in groups if group.thread_count == 4) 

    categories = get_queries(groups)
    x = np.arange(len(categories))

    for i, thread in enumerate(get_thread_counts(groups)):
        if thread != 4:
            continue

        elapsed_groups = defaultdict(lambda: list())
        scale_factors = get_scale_factors(groups)

        for query in categories:
            for group in [g for g in groups if g.thread_count == thread]:
                for i, sf in enumerate(scale_factors):
                    if group.query_name == query and group.scale_factor == sf:
                        elapsed_groups[sf].append(group.average_by("elapsed_time")*1000)
    
        fig, ax = plt.subplots(layout='constrained')

        width = 0.25  # the width of the bars
        multiplier = 0
        for idx, (attribute, measurement) in enumerate(reversed(elapsed_groups.items())):
            offset = width * multiplier
            rects = ax.bar(x + offset, measurement, width, hatch=hatch_patterns[idx % len(scale_factors)], label=attribute)
            # ax.bar_label(rects, padding=3)
            multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Query Elapsed Time(ms)')
        ax.set_xlabel('Query')
        ax.set_title(f'Elapsed Time varying on the scale factor (Thread={thread})')
        ax.set_xticks(x + width, categories)
        ax.legend(loc='upper left', ncols=1)
        ax.set_ylim(0, y_max*1.02)

        format = "pdf"
        out_path = get_plot_path(f"elapsed-query-time-thread{thread}", name, format)
        plt.savefig(out_path,
                format=format, bbox_inches="tight")

def plot_bar_thread_elapsed(groups: list[MeasurementGroup], name: str = "elapsed_plot_thread_bar"):
    y_max = max(group.average_by("elapsed_time")*1000 for group in groups)
    y_min = min(group.min_elapsed_time*1000 for group in groups) 

    categories = get_queries(groups)
    x = np.arange(len(categories))

    for i, scale_factor in enumerate(get_scale_factors(groups)):

        elapsed_groups = defaultdict(lambda: list())
        threads = get_thread_counts(groups)

        for query in categories:
            for group in [g for g in groups if g.scale_factor == scale_factor]:
                for i, thread in enumerate(threads):
                    if group.query_name == query and group.thread_count == thread:
                        elapsed_groups[thread].append(group.average_by("elapsed_time")*1000)
    
        fig, ax = plt.subplots(layout='constrained')

        width = 0.25  # the width of the bars
        multiplier = 0
        for idx, (attribute, measurement) in enumerate(elapsed_groups.items()):
            offset = width * multiplier
            rects = ax.bar(x + offset, measurement, width, hatch=hatch_patterns[idx % len(threads)], label=f"{attribute} Thread(s)")
            # ax.bar_label(rects, padding=3)
            multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Query Elapsed Time(ms)')
        ax.set_xlabel('Query')
        ax.set_title('Elapsed Time varying on the number of threads (SF=100)')
        ax.set_xticks(x + width, categories)
        ax.legend(loc='upper left', ncols=1)
        ax.set_ylim(0, y_max*1.02)

        format = "pdf"
        out_path = get_plot_path(f"elapsed-query-time-sf{scale_factor}", name, format)
        plt.savefig(out_path,
                format=format, bbox_inches="tight")

def  barplot_threads_rowscanned(groups: list[MeasurementGroup], name: str = "elapsed_bar"):
    normalize=1_000_000_000

    y_max = max(group.average_by_rows_scanned()/normalize for group in groups if group.thread_count == 4)

    categories = get_queries(groups)
    x = np.arange(len(categories))

    for i, thread in enumerate(get_thread_counts(groups)):
        if thread != 4:
            continue

        elapsed_groups = defaultdict(lambda: list())
        scale_factors = get_scale_factors(groups)

        for query in categories:
            for group in [g for g in groups if g.thread_count == thread]:
                for i, sf in enumerate(scale_factors):
                    if group.query_name == query and group.scale_factor == sf:
                        elapsed_groups[sf].append(group.average_by_rows_scanned()/normalize)
    
        fig, ax = plt.subplots(layout='constrained')

        width = 0.25  # the width of the bars
        multiplier = 0
        for idx, (attribute, measurement) in enumerate(reversed(elapsed_groups.items())):
            offset = width * multiplier
            ax.bar(x + offset, measurement, width, hatch=hatch_patterns[idx % len(scale_factors)], label=attribute)
            # ax.bar_label(rects, padding=3)
            multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Rows Scanned(Billion)')
        ax.set_xlabel('Query')
        ax.set_title(f'Accumulative Rows scanned (Thread={thread})')
        ax.set_xticks(x + width, categories)
        ax.legend(loc='upper left', ncols=1)
        ax.set_ylim(0, y_max*1.02)

        format = "pdf"
        out_path = get_plot_path(f"rows-scanned-bar-t{thread}", name, format)
        plt.savefig(out_path,
                format=format, bbox_inches="tight")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python plot.py <bench file path>")
        exit(1)

    measurements = read_data(sys.argv[1])

    groups = [MeasurementGroup(key=k, measurements=list(g)) for k, g in groupby(
        sorted(measurements, key=lambda x: x.get_name()), lambda x: x.get_name())]
    groups.sort(key=lambda x: x.key)

    queries = set([ "1.1", "2.2", "4.1" ])

    t1_groups_all = [g for g in groups if g.scale_factor == 100] # Only use quries with scale factor 100 since that is the only one that is common
    t2_groups_all = [g for g in groups if g.thread_count == 4] # Only use quries with 4 threads since that is the only one that is common
    t1_groups = [g for g in groups if g.scale_factor == 100 and g.query_name in queries] # Only use quries with scale factor 100 since that is the only one that is common
    t2_groups = [g for g in groups if g.thread_count == 4 and g.query_name in queries] # Only use quries with 4 threads since that is the only one that is common

    # General plot of elapsed times for all queries
    plot_elapsed(groups)
    plot_thread_elapsed(groups)
    # plot_scale_bar_elapsed(groups)

    # Graphs for experiment 1
    plot_bar_thread_elapsed(t1_groups_all) # Shows scaling based on increasing number of threads
    plot_thread_scale_elapsed(t1_groups, "t1_elapsed_line") # Shows elapsed time for queries 1.1, 2.2 and 4.1
    plot_thread_scale_rows(t1_groups, "t1-rows-scanned") # Shows rows scanned for queries 1.1, 2.2 and 4.1

    # Graphs for experiment 2
    plot_scale_bar_elapsed(t2_groups_all) # Shows scaling based on increasing scale factor
    plot_sf_elapsed(t2_groups, "t2_elapsed_line") # Shows elapsed time for queries 1.1, 2.2 and 4.1
    plot_sf_rows(t2_groups, "t2-rows-scanned") # Shows rows scanned for queries 1.1, 2.2 and 4.1
    barplot_threads_rowscanned(t2_groups, "t2-rows-scanned") # Shows scaling based on increasing number of threads
