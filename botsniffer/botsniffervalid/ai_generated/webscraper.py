import requests
from bs4 import BeautifulSoup

# Define the URL of the webpage to scrape
url = "https://example.com"  # Replace with the actual URL you want to scrape

# Send an HTTP GET request to fetch the content of the webpage
response = requests.get(url)

# If the request was successful (status code 200), proceed to parse the content
if response.status_code == 200:
    # Use BeautifulSoup to parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract all anchor ('a') tags from the HTML document
    links = soup.find_all('a')
    
    # Loop through each link and extract the href attribute (URL)
    for link in links:
        href = link.get('href')
        # Output each URL found on the page
        print(href)
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

