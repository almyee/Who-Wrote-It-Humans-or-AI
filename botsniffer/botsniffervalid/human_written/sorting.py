def bubble_sort(arr):
    # Sorts an array using the bubble sort algorithm.
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

if __name__ == "__main__":
    numbers = [64, 34, 25, 12, 22, 11, 90]
    print("Sorted List:", bubble_sort(numbers))

