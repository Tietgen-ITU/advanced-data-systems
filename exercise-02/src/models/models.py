from dataclasses import dataclass
from itertools import groupby
import json
from typing import Any


@dataclass
class Measurement:
    query_name: str
    thread_count: str
    scale_factor: str
    elapsed_time: float
    profile: Any

    @staticmethod
    def from_file(file: str):

        with open(file, 'r') as f:
            profilings = json.load(f)

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

    def average_by_rows_scanned(self):
        return sum([m.profile["cumulative_rows_scanned"] for m in self.measurements]) / len(self.measurements)
    
    def average_by_rows_cardinality(self):
        return sum([m.profile["cumulative_cardinality"] for m in self.measurements]) / len(self.measurements)

    def average_by(self, key: str):
        return sum([getattr(m, key) for m in self.measurements]) / len(self.measurements)

def read_data(file: str):
    measurements = Measurement.from_file(file)
    return measurements

def group_measurements(measurements: list[Measurement]):
    groups = [MeasurementGroup(key=k, measurements=list(g)) for k, g in groupby(
        sorted(measurements, key=lambda x: x.get_name()), lambda x: x.get_name())]
    groups.sort(key=lambda x: x.key)

    return groups

def get_queries(groups: list[MeasurementGroup]):
    return sorted(set(group.query_name for group in groups))


def get_thread_counts(groups: list[MeasurementGroup]):
    return sorted(set(group.thread_count for group in groups))


def get_scale_factors(groups: list[MeasurementGroup]):
    return sorted(set(group.scale_factor for group in groups))
