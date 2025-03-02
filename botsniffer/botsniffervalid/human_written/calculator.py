def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

if __name__ == "__main__":
    x, y = 10, 5
    print(f"Sum: {add(x, y)}")
    print(f"Difference: {subtract(x, y)}")
    print(f"Product: {multiply(x, y)}")
    print(f"Quotient: {divide(x, y)}")

