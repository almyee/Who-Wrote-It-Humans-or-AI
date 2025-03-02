# This script performs basic statistical analysis on numeric data.

import statistics
from typing import List, Dict

def compute_statistics(numbers: List[float]) -> Dict[str, float]:
    """
    Calculates basic statistics for a given dataset.

    Args:
        numbers (List[float]): A list of numerical values.

    Returns:
        Dict[str, float]: A dictionary containing mean, median, and standard deviation.
    """
    return {
        "mean": statistics.mean(numbers),
        "median": statistics.median(numbers),
        "std_dev": statistics.stdev(numbers) if len(numbers) > 1 else 0
    }

if __name__ == "__main__":
    dataset = [10, 20, 30, 40, 50]
    print("Statistical Results:", compute_statistics(dataset))

