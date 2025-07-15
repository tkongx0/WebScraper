import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

url = "https://SITEURL.com/blog/"

# Fetch the HTML content of the page
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# Parse the HTML using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Step 3: Find all blog post URLs
# Assuming blog post links are within 'a' tags with specific classes or attributes
blog_urls = []
for link in soup.find_all('a', href=True):
    # Check if the URL matches the pattern of blog posts (you can adjust this based on actual HTML structure)
    if "/blog/" in link['href'] and link['href'] != "/blog/":
        full_url = link['href']
        if not full_url.startswith("http"):  # Handle relative URLs
            full_url = f"https://hireveterans.com{full_url}"
        blog_urls.append(full_url)

# Print the extracted URLs
for idx, blog_url in enumerate(blog_urls, start=1):
    print(f"{idx}: {blog_url}")
