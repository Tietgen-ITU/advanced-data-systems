import matplotlib.pyplot as plt
import csv

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

# Function to create and save a bar chart
def plot_bar(categories, values, title="Bar Chart", xlabel="Categories", ylabel="Values", filename="bar_chart.png"):
    plt.figure(figsize=(8, 6))
    plt.bar(categories, values, color='g')
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

if __name__ == "__main__":
    data = []

    # Load data from a CSV file
    with open('./benchmark_sentiment_stats.csv', 'r') as file:
        reader = csv.reader(file, delimiter=';')
        for (repetition, query_type, elapsed_seconds, elapsed_milli) in reader:
            data.append((int(repetition), query_type, float(elapsed_seconds), int(elapsed_milli)))
        
    train_sql = [elapsed_seconds for _, query_type, elapsed_seconds, _ in data if query_type == "SQL_TRAIN"]
    predict_sql = [elapsed_seconds for _, query_type, elapsed_seconds, _ in data if query_type == "SQL_PREDICT"]
    train_udtf = [elapsed_seconds for _, query_type, elapsed_seconds, _ in data if query_type == "UDTF_TRAIN"]
    predict_udtf = [elapsed_seconds for _, query_type, elapsed_seconds, _ in data if query_type == "UDTF_PREDICT"]

    elapsed_train = [sum(train_udtf)/3, sum(train_sql)/3]

    # Plot a bar chart
    plot_bar(["UDTF", "SQL"], elapsed_train, title="UDTF vs. SQL Elapsed training time", xlabel="Query Type", ylabel="Elapsed Time (seconds)", filename="train_elapsed_seconds.png")

    elapsed_predict = [sum(predict_udtf)/3, sum(predict_sql)/3]
    plot_bar(["UDTF", "SQL"], elapsed_predict, title="UDTF vs. SQL Elapsed prediction time", xlabel="Query Type", ylabel="Elapsed Time (seconds)", filename="predict_elapsed_seconds.png")