import requests
from bs4 import BeautifulSoup

# Fetch BBC News page
url = "https://www.bbc.com/news"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Extract headlines
headlines = soup.find_all('h3')

print("Latest BBC News Headlines:")
for idx, headline in enumerate(headlines[:10]):  # Get top 10 headlines
    print(f"{idx+1}. {headline.text.strip()}")

