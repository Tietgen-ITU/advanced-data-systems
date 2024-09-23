import math
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import csv

markers = ['o', 's', '^', 'D', 'v']
line_styles = ['-', '--', '-.', ':', '-']

# Function to create and save a line plot
def plot_line(x, y, title="Line Plot", xlabel="X-axis", ylabel="Y-axis", filename="line_plot.png"):
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='b')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig(f"plots/{filename}", format='png')
    plt.close()  # Close the figure after saving

def plot_lines(x, ys, title="Line Plot", xlabel="X-axis", ylabel="Y-axis", max_y_value=0, filename="line_plot.png"):
    plt.figure(figsize=(8, 6))
    for index, key in enumerate(ys):
        data = ys[key]
        marker = markers[index]
        line_style = line_styles[index]
        plt.plot(x, data, marker=marker, linestyle=line_style, label=key)

    if max_y_value > 0:
        plt.ylim(0, max_y_value*1.1)

    plt.legend()
    plt.title(title, fontsize=20)
    plt.xlabel(xlabel, fontsize=16)
    plt.ylabel(ylabel, fontsize=16)
    plt.grid(True)
    plt.savefig(f"plots/{filename}", format='png')
    plt.close()  # Close the figure after saving

# Function to create and save a bar chart
def plot_bar(categories, values, title="Bar Chart", xlabel="Categories", ylabel="Values", filename="bar_chart.png"):
    plt.figure(figsize=(8, 6))
    plt.bar(categories, values)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig(f"plots/{filename}", format='png')
    plt.close()  # Close the figure after saving

# Function to create and save a scatter plot
def plot_scatter(x, y, title="Scatter Plot", xlabel="X-axis", ylabel="Y-axis", filename="scatter_plot.png"):
    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, color='r')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig(f"plots/{filename}", format='png')
    plt.close()  # Close the figure after saving

# Function to create and save a histogram
def plot_histogram(data, bins=10, title="Histogram", xlabel="Values", ylabel="Frequency", filename="histogram.png"):
    plt.figure(figsize=(8, 6))
    plt.hist(data, bins=bins, color='purple')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.savefig(f"plots/{filename}", format='png')
    plt.close()  # Close the figure after saving

def logarithmic_normalization(data):
    return np.log(data+1e-10)

if __name__ == "__main__":
    id_to_query = {0: 1, 1: 5, 2: 18}
    warehouse_sizes = ['X-Small', 'Small', 'Medium', 'Large']
    schemas = ['TPCH_SF1', 'TPCH_SF10', 'TPCH_SF100', 'TPCH_SF1000']

    data = []

    # Load data from a CSV file
    with open('./benchmark_stats.csv', 'r') as file:
        reader = csv.reader(file, delimiter=';')
        for (qid, tpch_query_id, database, warehouse_size, elapsed_seconds, elapsed_milli) in reader:
            data.append((id_to_query[int(tpch_query_id)], database, warehouse_size, float(elapsed_seconds), int(elapsed_milli)))
        
    queries_elapsed = defaultdict(lambda: list())
    for tpch_qid, schema, warehouse_size, elapsed_seconds, elapsed_milli in data:
        queries_elapsed[(tpch_qid, schema, warehouse_size)].append((elapsed_seconds, elapsed_milli))

    queries_aggregated_elapsed = {}
    for wh in warehouse_sizes:
        for schema in schemas:
            for _, qid in id_to_query.items():
                benchmarks = queries_elapsed[(qid, schema, wh)]
                if len(benchmarks) > 0:
                    elapsed_seconds = sum([b[0] for b in benchmarks]) / len(benchmarks)
                    elapsed_milli = sum([b[1] for b in benchmarks]) / len(benchmarks)
                    queries_aggregated_elapsed[(qid, schema, wh)] = elapsed_milli
    

    # Plot the average elapsed time for each query in each schema and warehouse size
    query_benchmarks = {}
    for _,qid in id_to_query.items():
        dwh = defaultdict(lambda: list())
        for schema in schemas:
            for wh in warehouse_sizes:
                if (qid, schema, wh) not in queries_aggregated_elapsed:
                    continue
                value = queries_aggregated_elapsed[(qid, schema, wh)]
                dwh[wh].append(math.log(value))
        
        query_benchmarks[qid] = dwh

    # Get the maximum elapsed time to set the y-axis limit
    max_y_value = max([max([max(v) for v in query_benchmarks[qid].values()]) for qid in query_benchmarks])
    for qid, dwh in query_benchmarks.items():
        plot_lines(schemas, 
                dwh, 
                title=f"Query {qid} Elapsed Time", 
                xlabel="Schema (Scaling Factor)", 
                ylabel="Log Normalized Elapsed Time (ms)", 
                max_y_value=max_y_value,
                filename=f"query_{qid}_elapsed_time.png")