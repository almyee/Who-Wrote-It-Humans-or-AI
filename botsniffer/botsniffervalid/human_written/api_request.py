import requests

def fetch_data(url):
    # Fetches data from the given URL.
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

if __name__ == "__main__":
    data = fetch_data("https://jsonplaceholder.typicode.com/todos/1")
    print("Fetched Data:", data)

