from collections.abc import Callable
from typing import Any

type PropFetcher = Callable[[list[Any]], tuple[str, float]]

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

def create_avg_propfetcher(name: str) -> PropFetcher:
    def fetcher(items: list[Any]) -> tuple[str, float]:
        return (name, get_float_property(name, items)) 

    return fetcher