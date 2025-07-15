from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import time

# Setup ChromeDriver path (replace with your actual path)
chrome_driver_path = 'C:\\Users\\TouKong\\AppData\\Roaming\\Python\\Python311\\site-packages\\chromedriver-win64\\chromedriver.exe'
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Example list of blog URLs
blog_urls = [
    "https://SITEURL.com/blog/TEST1",
    # Add other blog URLs here...
]

# Function to extract content from a single blog URL
def extract_blog_content(url):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    # Extract page source using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Extract the blog title
    title = soup.find('h1').text.strip() if soup.find('h1') else 'No Title'

    # Extract the blog content (adjust selectors as needed)
    content_div = soup.find('div', class_='post-content')  # Adjust the class or tag as needed
    blog_content = content_div.get_text(separator='\n').strip() if content_div else 'No Content'

    # Extract all image URLs in the blog post
    images = content_div.find_all('img') if content_div else []
    image_urls = [img['src'] for img in images if 'src' in img.attrs]

    # Extract category from breadcrumb structure
    category = 'Uncategorized'  # Default category

    # Locate the breadcrumb <div> element containing "Blog > [Category]"
    breadcrumb_div = soup.find('div', class_='blog__full-article__breadcrumb')
    
    if breadcrumb_div:
        # Extract the second <a> tag text which is the category
        breadcrumb_links = breadcrumb_div.find_all('a')
        if len(breadcrumb_links) > 1:
            category = breadcrumb_links[1].text.strip()

    return {
        'title': title,
        'content': blog_content,
        'images': image_urls,
        'category': category
    }

# Function to create WordPress XML structure
def create_wordpress_xml(blog_data_list):
    # Create root element 'rss' with namespaces
    rss = ET.Element('rss', version='2.0', attrib={'xmlns:excerpt': 'http://wordpress.org/export/1.2/excerpt/',
                                                   'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
                                                   'xmlns:wfw': 'http://wellformedweb.org/CommentAPI/',
                                                   'xmlns:dc': 'http://purl.org/dc/elements/1.1/',
                                                   'xmlns:wp': 'http://wordpress.org/export/1.2/'})
    
    # Create 'channel' element
    channel = ET.SubElement(rss, 'channel')

    # Add channel title, link, and description
    ET.SubElement(channel, 'title').text = "Your Blog Title"  # Replace with your blog's title
    ET.SubElement(channel, 'link').text = "https://yourblog.com"  # Replace with your blog's URL
    ET.SubElement(channel, 'description').text = "Blog imported from another site."

    # Add each blog post as an item
    for blog in blog_data_list:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = blog['title']
        ET.SubElement(item, 'link').text = "https://yourblog.com/blog/" + blog['title'].replace(' ', '-').lower()
        ET.SubElement(item, 'content:encoded').text = blog['content']

        # Add images (as URLs, you may need to handle media uploads separately)
        for image_url in blog['images']:
            ET.SubElement(item, 'wp:attachment_url').text = image_url
        
        # Add category
        category_element = ET.SubElement(item, 'category', domain='category', nicename=blog['category'].lower().replace(' ', '-'))
        category_element.text = blog['category']

    # Create an ElementTree object
    tree = ET.ElementTree(rss)

    # Write the XML to a file
    tree.write('wordpress_import.xml', encoding='utf-8', xml_declaration=True)

    print("WordPress XML file created successfully!")

# List to hold extracted blog data
all_blog_data = []

# Extract content for each blog
for url in blog_urls:
    blog_data = extract_blog_content(url)
    all_blog_data.append(blog_data)

# Close the browser
driver.quit()

# Create WordPress XML file from extracted data
create_wordpress_xml(all_blog_data)

print("Blog scraping and XML generation complete!")
