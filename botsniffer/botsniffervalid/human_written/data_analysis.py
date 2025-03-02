import statistics

def analyze_data(data):
    """Returns basic statistics for a given list of numbers."""
    return {
        "mean": statistics.mean(data),
        "median": statistics.median(data),
        "std_dev": statistics.stdev(data)
    }

if __name__ == "__main__":
    values = [10, 20, 30, 40, 50]
    print("Statistics:", analyze_data(values))

