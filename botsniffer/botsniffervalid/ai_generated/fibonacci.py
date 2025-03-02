# This script calculates Fibonacci numbers.

from typing import List

def generate_fibonacci_sequence(count: int) -> List[int]:
    """
    Generates a list of Fibonacci numbers.
    
    Args:
        count (int): The number of Fibonacci numbers to generate.
    
    Returns:
        List[int]: A list containing the Fibonacci sequence.
    """
    if count <= 0:
        return []
    
    sequence = [0, 1]
    while len(sequence) < count:
        sequence.append(sequence[-1] + sequence[-2])
    
    return sequence

if __name__ == "__main__":
    print(generate_fibonacci_sequence(10))

