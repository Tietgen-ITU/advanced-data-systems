from collections import defaultdict
import pathlib
import sys
from dataclasses import dataclass
import time

from matplotlib import pyplot as plt
import numpy as np
from models.models import *
from models.operator import *

@dataclass
class OperatorMeasurementGroup:
    scale: int
    thread: int
    query_name: str
    measurements: dict

    def __init__(self, query_name, scale, threads):
        self.scale = scale
        self.thread = threads
        self.query_name = query_name
        self.measurements = {}

    def add_operator_measurement(self, operator_name:str, operator_measurement: dict):
        if operator_name not in self.measurements:
            self.measurements[operator_name] = operator_measurement
            return
        
        for metric_name, _ in self.measurements[operator_name].items():
            self.measurements[operator_name][metric_name] += operator_measurement[metric_name]
    
    def get_operator_measurement(self, operator_name:str) -> list[dict]:
        return self.measurements[operator_name]
    
    def get_max_measurement(self, operator_name:str) -> float:
        return max([self.measurements[k][operator_name] for k in self.measurements.keys()])/self.thread

def get_operator_measurments(measurement_groups: list[MeasurementGroup], prop_names: list[PropFetcher]) -> list[OperatorMeasurementGroup]:

    groups = []   
    for measurement_group in measurement_groups:
        m = parse_measurement(measurement_group, prop_names)
        groups.append(m)
    
    return groups

def parse_measurement(measurementgroup: MeasurementGroup, prop_names: list[PropFetcher]) -> OperatorMeasurementGroup:
    operator_group = OperatorMeasurementGroup(measurementgroup.query_name, measurementgroup.scale_factor, measurementgroup.thread_count)
    operator_tree_root = [m.profile["children"][0] for m in measurementgroup.measurements]

    return parse_operator(operator_tree_root, prop_names, operator_group)

def parse_operator(operators: list[Any], prop_names: list[PropFetcher], omg: OperatorMeasurementGroup) -> OperatorMeasurementGroup:

    operator_name = get_string_property("operator_type", operators)
    properties = {prop: value for prop, value in [fetcher(operators) for fetcher in prop_names]}

    omg.add_operator_measurement(operator_name, properties)
    
    if has_property("children", operators):
        for child in get_list_property("children", operators):
            parse_operator(child, prop_names, omg)
    
    return omg

def print_group_stats(operators):

    print(operators)
    print(operators[0].scale)
    print(len(operators))

markers = ['o', 's', 'D', '^', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 'x']
line_styles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--', '-.', ':', '-']
hatch_patterns = ['///', '\\\\', '...', '/', '\\', '-', 'O' ]

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
    
def plot_bar_for_group(query_name, fixed_name, data, x_label, labels, title, y_max, plot_type_name):
    # print(data)

    # for key, value in data.items():
    #     print(f"{key}: {value}")

    categories = x_label
    x = np.arange(len(categories))
    
    fig, ax = plt.subplots(layout='constrained')

    width = 0.25  # the width of the bars
    multiplier = 0
    for idx, (attribute, measurement) in enumerate(data.items()):
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, hatch=hatch_patterns[idx % len(labels)], label=labels[idx % len(labels)])
        # ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Operator Elapsed Time(s)', fontsize=16)
    ax.set_xlabel('Operator Type', fontsize=16)
    ax.set_title(title, fontsize=18)
    ax.set_xticks(x + width, categories, rotation=17, fontsize=14)
    plt.yticks(fontsize=14)
    ax.legend(loc='upper left', ncols=1)
    ax.set_ylim(0, y_max*1.01)

    format = "pdf"
    out_path = get_plot_path(f"elapsed-operator-fixed-{fixed_name}-q{query_name}", plot_type_name, format)
    plt.savefig(out_path,
            format=format, bbox_inches="tight")

def plot_fixed_scale_bar(groups: list[OperatorMeasurementGroup], name: str = "operator_fixed_scale_elapsed"):
    metric = "operator_timing"
    y_max = max([g.get_max_measurement(metric) for g in groups])

    query_types = set([g.query_name for g in groups])
    group_query = {q: [g for g in groups if g.query_name == q] for q in query_types}


    for query, group in group_query.items():
        x_labels = [op for op in group[0].measurements.keys()]

        elapsed_groups = defaultdict(lambda: list())
        threads = [1, 4, 8]

        labels = [f"{thread} Thread(s)" for thread in threads]

        for op_type in x_labels:
            for i, thread in enumerate(threads):
                for gm in group:
                    if gm.thread == thread:
                        elapsed_groups[thread].append(gm.measurements[op_type]["operator_timing"]/thread)

        plot_bar_for_group(query, "sf", elapsed_groups, x_labels, labels=labels, title=f'Elapsed time for each operator type in query {query}(SF=100)', y_max=y_max, plot_type_name=name)

def plot_fixed_thread_bar(groups: list[OperatorMeasurementGroup], name: str = "operator_fixed_thread_elapsed"):
    metric = "operator_timing"
    y_max = max([g.get_max_measurement(metric) for g in groups])

    query_types = set([g.query_name for g in groups])
    group_query = {q: [g for g in groups if g.query_name == q] for q in query_types}


    for query, group in group_query.items():
        x_labels = [op for op in group[0].measurements.keys()]

        elapsed_groups = defaultdict(lambda: list())
        scale_factors = [1, 10, 100]

        labels = [f"{sf} SF" for sf in scale_factors]

        for op_type in x_labels:
            for i, sf in enumerate(scale_factors):
                for gm in group:
                    if gm.scale == sf:
                        if op_type == "FILTER" and op_type not in gm.measurements:
                            elapsed_groups[sf].append(0)
                            continue

                        elapsed_groups[sf].append(gm.measurements[op_type][metric]/gm.thread)

        plot_bar_for_group(query, "threads", elapsed_groups, x_labels, labels=labels, title=f'Elapsed time for each operator type in query {query}(Threads=4)', y_max=y_max, plot_type_name=name)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python plot.py <bench file path>")
        exit(1)

    queries = set([ "1.1", "2.2", "4.1" ])

    measurements = read_data(sys.argv[1])
    groups = [group for group in group_measurements(measurements) if group.query_name in queries] # Only focus on specific queries

    operator_measurements = get_operator_measurments(groups, [
        create_avg_propfetcher("operator_timing"),
        create_avg_propfetcher("operator_rows_scanned"),
        create_avg_propfetcher("operator_cardinality")
    ])

    operator_fixed_threads = [group for group in operator_measurements if group.thread == 4]
    operator_fixed_scale = [group for group in operator_measurements if group.scale == 100]

    plot_fixed_thread_bar(operator_fixed_threads)
    plot_fixed_scale_bar(operator_fixed_scale)

    # print_group_stats(operator_fixed_threads)
    # print_group_stats(operator_fixed_scale)

    # print(len(groups))