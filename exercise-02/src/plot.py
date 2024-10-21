from itertools import groupby
import json
import pathlib
import sys
from typing import Any
import matplotlib.pyplot as plt
from dataclasses import dataclass

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

def plot_elapsed(groups: list[MeasurementGroup]):
    # y_max = max(max(m.elapsed_time for m in c.measurements) for c in configs)

    for query_name in get_queries(groups):
        plt.figure()
        ax = plt.gca()

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

        if not (CURRENT_WORKING_DIRECTORY / "output").exists():
            (CURRENT_WORKING_DIRECTORY / "output").mkdir()
        if not (CURRENT_WORKING_DIRECTORY / "output" / format).exists():
            (CURRENT_WORKING_DIRECTORY / "output" / format).mkdir()

        out_path = CURRENT_WORKING_DIRECTORY / "output" / format / f"elapsed-q{query_name}.{format}"
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

    plot_elapsed(groups)
