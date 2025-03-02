import os

def read_file(filename):
    # Reads a file and returns its contents as a string.
    if not os.path.exists(filename):
        return "File not found."
    with open(filename, 'r') as file:
        return file.read()

def write_file(filename, content):
    # Writes content to a file.
    with open(filename, 'w') as file:
        file.write(content)

if __name__ == "__main__":
    file_name = "example.txt"
    write_file(file_name, "Hello, this is a test file.")
    print(read_file(file_name))

