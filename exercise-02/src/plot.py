from collections import defaultdict
from itertools import groupby
import json
import pathlib
import sys
from typing import Any
import matplotlib.pyplot as plt
from dataclasses import dataclass

import numpy as np

CURRENT_WORKING_DIRECTORY = pathlib.Path(__file__).parent.resolve()

markers = ['o', 's', '^', 'D', 'v']
line_styles = ['-', '--', '-.', ':', '-']



@dataclass
class Measurement:
    query_name: str
    thread_count: str
    scale_factor: str
    elapsed_time: float
    profile: Any

    @staticmethod
    def from_file(file: str):
        profilings = []
        with open(file) as f:
            buffer = []

            for line in f:
                buffer.append(line)

                if line.rstrip() == "}":
                    profile = json.loads(''.join(buffer))
                    profilings.append(profile)
                    buffer.clear()

        measurements = []
        for profile in profilings:
            q_str = profile["benchmark_name"]
            measurements.append(Measurement(
                query_name=q_str.replace("Q", "").replace("v", ".")[3:6],
                scale_factor=profile["scale_factor"],
                thread_count=profile["thread_count"],
                elapsed_time=profile["operator_timing"],
                profile=profile
            ))

        return measurements

    def get_name(self):
        return self.profile["benchmark_name"]

@dataclass
class MeasurementGroup:
    key: str
    measurements: list[Measurement]
    query_name: str = ""
    thread_count: int = -1
    scale_factor: int = -1

    def __post_init__(self):
        self.query_name = self.measurements[0].query_name
        self.thread_count = int(self.measurements[0].thread_count)
        self.scale_factor = int(self.measurements[0].scale_factor)

        self.min_elapsed_time = min(m.elapsed_time for m in self.measurements)
        self.max_elapsed_time = max(m.elapsed_time for m in self.measurements)

    def average_by(self, key: str):
        return sum([getattr(m, key) for m in self.measurements]) / len(self.measurements)

def read_data(file: str):
    measurements = Measurement.from_file(file)
    return measurements

def get_queries(groups: list[MeasurementGroup]):
    return sorted(set(group.query_name for group in groups))


def get_thread_counts(groups: list[MeasurementGroup]):
    return sorted(set(group.thread_count for group in groups))


def get_scale_factors(groups: list[MeasurementGroup]):
    return sorted(set(group.scale_factor for group in groups))

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

def plot_scale_bar_elapsed(groups: list[MeasurementGroup], name: str = "elapsed_bar"):
    y_max = max(group.max_elapsed_time*1000 for group in groups)
    y_min = min(group.min_elapsed_time*1000 for group in groups)

    categories = get_queries(groups)
    x = np.arange(len(categories))

    for i, thread in enumerate(get_thread_counts(groups)):
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
        for attribute, measurement in elapsed_groups.items():
            offset = width * multiplier
            rects = ax.bar(x + offset, measurement, width, label=attribute)
            ax.bar_label(rects, padding=3)
            multiplier += 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Query Elapsed Time(ms)')
        ax.set_title('Scale Factors Elapsed Time for each Query')
        ax.set_xticks(x + width, categories)
        ax.legend(loc='upper left', ncols=3)
        ax.set_ylim(0, y_max*1.1)

        format = "pdf"
        out_path = get_plot_path(f"elapsed-query-time-thread{thread}", name, format)
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

    # t1_groups = [g for g in groups if g.scale_factor == 10] # Only use quries with scale factor 10 since that is the only one that is common
    t2_groups = [g for g in groups if g.thread_count == 1] # Only use quries with 4 threads since that is the only one that is common

    # General plot of elapsed times for all queries
    plot_elapsed(groups)
    plot_scale_bar_elapsed(groups)
