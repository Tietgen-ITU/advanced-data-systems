from dataclasses import dataclass
import os
import pathlib
import sys
from typing import List
import json
from matplotlib import pyplot as plt

# Define dataclasses
@dataclass
class Measurement:
    Optimization: int
    Execution: int
    Post_processing: int
    par_ex_000: int
    par_ex_000_upper_estimate: int
    par_ex_000_lower_estimate: int
    par_ex_001: int
    par_ex_001_upper_estimate: int
    par_ex_001_lower_estimate: int
    Estimate_1_lower: int
    Estimate_1_upper: int
    Measured_cost_upper: float
    Measured_cost_lower: float
    Estimated_costs_1_upper: float
    Estimated_costs_1_lower: float

    @staticmethod
    def from_json(json):
        return Measurement(
                Optimization=json["Optimization"],
                Execution=json["Execution"],
                Post_processing=json["Post-processing"],
                par_ex_000=json["par-ex-000"],
                par_ex_000_upper_estimate=json["par-ex-000-upper-estimate"],
                par_ex_000_lower_estimate=json["par-ex-000-lower-estimate"],
                par_ex_001=json["par-ex-001"],
                par_ex_001_upper_estimate=json["par-ex-001-upper-estimate"],
                par_ex_001_lower_estimate=json["par-ex-001-lower-estimate"],
                Estimate_1_lower=json["Estimate 1 (lower)"],
                Estimate_1_upper=json["Estimate 1 (upper)"],
                Measured_cost_upper=json["Measured cost-upper"],
                Measured_cost_lower=json["Measured cost-lower"],
                Estimated_costs_1_upper=json["Estimated costs (1)-upper"],
                Estimated_costs_1_lower=json["Estimated costs (1)-lower"]
            )


@dataclass
class Dataset:
    name: str
    workload: str
    projection: bool
    filepath: str
    file_type: str
    measurements: List[Measurement]

    def get_average_execution_time(self):
        return sum([measurement.Execution for measurement in self.measurements]) / len(self.measurements)

    @staticmethod
    def from_jsonfile(file: str):
        with open(file, 'r') as f:
            json_objs = json.load(f)

        return [Dataset.from_json(obj) for obj in json_objs] 

    @staticmethod
    def from_json(json):
        file_path = json["filepath"]
        file_name, extension = os.path.splitext(os.path.basename(file_path))

        name_parts = json["name"].split("-")
        has_projection = "projection" in name_parts
        file_extension = extension[1:]  # Remove the dot from the extension

        return Dataset(
            name=f"{file_name}-{file_extension}-projection" if has_projection else f"{file_name}-{file_extension}",
            workload=name_parts[0],
            projection=has_projection,
            filepath=json["filepath"],
            file_type=file_extension,
            measurements=[ Measurement.from_json(measurement) for measurement in json["measurements"] ]
        )
CURRENT_WORKING_DIRECTORY = pathlib.Path(__file__).parent.resolve()

def get_plot_path(plot_name: str, group_name: str, format: str):
    if not (CURRENT_WORKING_DIRECTORY / "output").exists():
        (CURRENT_WORKING_DIRECTORY / "output").mkdir()
    if not (CURRENT_WORKING_DIRECTORY / "output" / format).exists():
        (CURRENT_WORKING_DIRECTORY / "output" / format).mkdir()
    if not (CURRENT_WORKING_DIRECTORY / "output" / format / group_name).exists():
        (CURRENT_WORKING_DIRECTORY / "output" / format / group_name).mkdir()

    out_path = CURRENT_WORKING_DIRECTORY / "output" / format / group_name / f"{plot_name}.{format}"
    return out_path

if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print("Usage: python plot.py <bench file path>")
        exit(1)

    benchmarks = Dataset.from_jsonfile(sys.argv[1])

    average_execution_times = [
    (
        dataset.name,
        dataset.get_average_execution_time() / 1000
    ) for dataset in benchmarks ]

    sorted(average_execution_times, key=lambda x: x[0])  # Sort by average execution time
    
    names, avg_times = zip(*average_execution_times)  # Separate names and execution times
    plt.figure(figsize=(10, 6))
    plt.bar(names, avg_times, color='skyblue')
    plt.title('Average Execution Time for Workloads', fontsize=14)
    plt.xlabel('Workload name', fontsize=12)
    plt.ylabel('Average Execution Time (s)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Print the result
    for dataset in benchmarks:
        print(dataset)

    format = "pdf"
    out_path = get_plot_path("elapsed", "avg-bar", format)
    plt.savefig(out_path,
            format=format, bbox_inches="tight")
