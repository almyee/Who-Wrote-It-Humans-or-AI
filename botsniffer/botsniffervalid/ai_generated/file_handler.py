# This script manages file operations such as reading and writing.

import os

def read_from_file(file_path: str) -> str:
    """
    Reads the contents of a file and returns them as a string.
    
    Args:
        file_path (str): Path to the file to be read.
    
    Returns:
        str: File contents or an error message.
    """
    if not os.path.isfile(file_path):
        return "Error: The specified file does not exist."
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_to_file(file_path: str, content: str) -> None:
    """
    Writes the provided content to a specified file.
    
    Args:
        file_path (str): Path to the file to be written to.
        content (str): Content to be written.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

if __name__ == "__main__":
    file_name = "test_document.txt"
    write_to_file(file_name, "This is an AI-generated file content.")
    print(read_from_file(file_name))

