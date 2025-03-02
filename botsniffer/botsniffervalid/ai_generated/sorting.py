# This script implements a basic sorting algorithm (Bubble Sort).

from typing import List

def bubble_sort_algorithm(input_list: List[int]) -> List[int]:
    """
    Performs a bubble sort on the input list.
    
    Args:
        input_list (List[int]): A list of integers to be sorted.
    
    Returns:
        List[int]: The sorted list in ascending order.
    """
    length = len(input_list)
    for i in range(length):
        for j in range(length - i - 1):
            if input_list[j] > input_list[j + 1]:
                input_list[j], input_list[j + 1] = input_list[j + 1], input_list[j]
    return input_list

if __name__ == "__main__":
    sample_numbers = [64, 34, 25, 12, 22, 11, 90]
    print("Sorted List:", bubble_sort_algorithm(sample_numbers))

