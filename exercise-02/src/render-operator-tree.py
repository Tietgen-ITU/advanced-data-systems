import sys
from models.tree import TreeNode
from models.models import *
from models.operator import *

def parse_measurement(measurementgroup: MeasurementGroup, prop_names: list[PropFetcher]) -> TreeNode:
    operator_tree_root = [m.profile["children"][0] for m in measurementgroup.measurements]

    return parse_operator(operator_tree_root, prop_names)

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

if __name__ == "__main__":
    measurements = read_data(sys.argv[1])
    props_to_display = [
        create_avg_propfetcher("operator_timing"),
        create_avg_propfetcher("operator_rows_scanned"),
        create_avg_propfetcher("operator_cardinality")
    ]

    tree_root = parse_measurement(group_measurements(measurements)[0], props_to_display)

    print(tree_root.render())