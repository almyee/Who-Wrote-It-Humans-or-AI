# This script retrieves data from an API endpoint.

import requests

def get_api_data(endpoint: str) -> dict:
    """
    Fetches JSON data from an API.

    Args:
        endpoint (str): The URL of the API endpoint.

    Returns:
        dict: The retrieved JSON data or an empty dictionary.
    """
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {}

if __name__ == "__main__":
    api_url = "https://jsonplaceholder.typicode.com/todos/1"
    print("API Response:", get_api_data(api_url))

