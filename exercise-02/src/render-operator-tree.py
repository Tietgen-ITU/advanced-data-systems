import sys
from typing import Callable
from models.tree import TreeNode
from models.models import *

type PropFetcher = Callable[[list[Any]], tuple[str, float]]

def parse_measurement(measurementgroup: MeasurementGroup, prop_names: list[PropFetcher]) -> TreeNode:
    operator_tree_root = [m.profile["children"][0] for m in measurementgroup.measurements]

    return parse_operator(operator_tree_root, prop_names)

def get_property(name: str, items: list[Any]) -> list[Any]:
    return [properties[name] for properties in items]

def get_list_property(name: str, items: list[Any]) -> list[list[Any]]:
    measurement_items = get_property(name, items)
    prop_items = []

    for value_index, _ in enumerate(measurement_items[0]):
        values = [measurement_items[i][value_index] for i in range(len(measurement_items))]
        prop_items.append(values)

    return prop_items

def get_string_property(name: str, items: list[Any]) -> str:

    values = get_property(name, items)
    value = values[0]

    if not all(v == value for v in values):
        print("Warning: Multiple values found for property", name)
        exit(1)
    
    return value

def get_float_property(name: str, items: list[Any]) -> float:

    values = get_property(name, items)

    return sum(values) / len(values)

def has_property(name: str, items: list[Any]) -> bool:

    return all(name in properties for properties in items)

def parse_operator(operators: list[Any], prop_names: list[PropFetcher]) -> TreeNode:

    operator_name = get_string_property("operator_type", operators)
    properties = {prop: value for prop, value in [fetcher(operators) for fetcher in prop_names]}

    if operator_name == "TABLE_SCAN":
        operator_details = get_property("extra_info", operators)
        operator_name = f"{operator_name} ({get_string_property('Text', operator_details)})"
        has_filter = has_property("Filters", operator_details)
        has_projection = has_property("Projections", operator_details)

        properties["projection"] = has_projection
        properties["filter"] = has_filter
    
    node = TreeNode(operator_name, properties)

    if has_property("children", operators):
        for child in get_list_property("children", operators):
            node.children.append(parse_operator(child, prop_names))
    
    return node

def create_avg_propfetcher(name: str) -> PropFetcher:
    def fetcher(items: list[Any]) -> tuple[str, float]:
        return (name, get_float_property(name, items)) 

    return fetcher

if __name__ == "__main__":
    measurements = read_data(sys.argv[1])
    props_to_display = [
        create_avg_propfetcher("operator_timing"),
        create_avg_propfetcher("operator_rows_scanned"),
        create_avg_propfetcher("operator_cardinality")
    ]

    tree_root = parse_measurement(group_measurements(measurements)[0], props_to_display)

    print(tree_root.render())