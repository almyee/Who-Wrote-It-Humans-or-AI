# This program performs basic arithmetic operations.

def add_numbers(number1: float, number2: float) -> float:
    """Adds two numbers together."""
    return number1 + number2

def subtract_numbers(number1: float, number2: float) -> float:
    """Subtracts the second number from the first."""
    return number1 - number2

def multiply_numbers(number1: float, number2: float) -> float:
    """Multiplies two numbers together."""
    return number1 * number2

def divide_numbers(number1: float, number2: float) -> float:
    """Divides the first number by the second. Raises an error if division by zero is attempted."""
    if number2 == 0:
        raise ZeroDivisionError("Division by zero is not allowed.")
    return number1 / number2

if __name__ == "__main__":
    num1, num2 = 10, 5
    print(f"Addition Result: {add_numbers(num1, num2)}")
    print(f"Subtraction Result: {subtract_numbers(num1, num2)}")
    print(f"Multiplication Result: {multiply_numbers(num1, num2)}")
    print(f"Division Result: {divide_numbers(num1, num2)}")

