from datetime import datetime
import os
import json
import requests  # To make HTTP requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
from requests.auth import HTTPBasicAuth  # For basic authentication

#WP API creds
WORDPRESS_SITE = "https://admin.SITEURL.com/wp-json/wp/v2/"
USERNAME = "EMAIL"
APPLICATION_PASSWORD = "PASSWORD"

#Setup ChromeDriver path - emulates a browser
chrome_driver_path = 'C:\\Users\\TouKong\\AppData\\Roaming\\Python\\Python311\\site-packages\\chromedriver-win64\\chromedriver.exe'
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service)

#Blog URLs
#Path to text file containing the blog URLs
file_path = r"C:\\Users\\TouKong\\Desktop\\VS Code Projects\\Hire Veterans\\blog_url_list_8.txt"
blog_urls = []

#Read file and store each line as a URL in the blog_urls list
with open(file_path, 'r') as file:
    for line in file:
        clean_url = line.strip().strip('",')  #Remove leading/trailing quotes or commas
        if clean_url:
            blog_urls.append(clean_url)

print(f'Cleaned/accounted {len(blog_urls)} blog URLs.')

# blog_urls = [
#     "https://hireveterans.com/blog/aims-community-college-joins-hireveterans",
#     "https://hireveterans.com/blog/professions-expected-to-grow-in-the-future-for-transitioning-veterans"
# ]

#Extract content from a single blog URL
def extract_blog_content(url):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    #Extract page source using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    #Extract Title
    title_element = soup.find('h1', class_='title__primary title__centered')
    title = title_element.get_text(strip=True) if title_element else 'No Title Found'

    #Extract Date
    date_element = soup.find('div', class_='blog__content--date')
    date = date_element.get_text(strip=True) if date_element else 'No Date Found'

    #Extract Blog Content
    blog_content_element = soup.find('div', class_='blog__content')
    blog_content = ""
    if blog_content_element:
        #Extract paragraphs, headings, etc. within blog content
        for element in blog_content_element.find_all(['p', 'h2', 'h3', 'h4', 'h5', 'h6']):
            blog_content += str(element)

    #Extract Images
    images = []
    for img_tag in soup.select('.blog__content--image img'):
        img_url = img_tag.get('src')
        if img_url:
            images.append(img_url)

    #Extract category from breadcrumb structure
    category = 'Uncategorized'  # Default category

    #Locate the breadcrumb <div> element containing "Blog > [Category]"
    breadcrumb_div = soup.find('div', class_='blog__full-article__breadcrumb')
    if breadcrumb_div:
        breadcrumb_links = breadcrumb_div.find_all('a')
        if len(breadcrumb_links) > 1:
            category = breadcrumb_links[1].text.strip()

    return {
        'title': title,
        'date': date,
        'content': blog_content,
        'images': images,
        'category': category
    }

#Upload an image to WordPress and return the image ID
def upload_image_to_wordpress(image_url):
    try:
        #Download image
        response = requests.get(image_url)
        response.raise_for_status()  # Check if the request was successful
        
        #Get image filename
        image_name = os.path.basename(image_url)
        
        #Prep headers
        headers = {
            'Content-Disposition': f'attachment; filename="{image_name}"',
        }

        #Prep file upload
        files = {'file': (image_name, response.content, 'image/jpeg')}  #Adjust MIME type as needed

        #Upload image to WordPress
        res = requests.post(
            f"{WORDPRESS_SITE}media",
            headers=headers,
            files=files,
            auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
        )
        res.raise_for_status()  #Raise an error if the upload fails
        
        #Return uploaded image ID
        image_id = res.json()['id']
        print(f"Image '{image_name}' uploaded successfully. Media ID: {image_id}")
        return image_id

    except Exception as e:
        print(f"Failed to upload image {image_url}: {e}")
        return None
    
#Convert date to ISO 8601 format for WordPress
def convert_to_iso8601(date_str):
    try:
        return datetime.strptime(date_str, '%b %d, %Y').isoformat()
    except ValueError:
        print(f"Error: Could not convert date '{date_str}' to ISO 8601 format.")
        return None

#Serialize Gutenberg blocks for WordPress
def serialize_blocks(blocks):
    serialized_blocks = []
    for block in blocks:
        attrs = json.dumps(block['attrs']) if block['attrs'] else ''
        serialized_block = f"<!-- wp:{block['blockName']} {attrs} -->{block['innerHTML']}<!-- /wp:{block['blockName']} -->"
        serialized_blocks.append(serialized_block)
    return "".join(serialized_blocks)

#Create a post in WordPress using Gutenberg blocks
def create_post_in_wordpress(blog_data):
    #Prep post data
    post_data = {
        'title': blog_data['title'],
        'content': '',
        'status': 'publish',  #'draft' to save as draft or 'publish' to publish immediately
        'author': 1,  #Set author to user_id 1 for admin
    }

    #Convert date to WordPress-compatible format
    post_data['date'] = convert_to_iso8601(blog_data['date']) if 'date' in blog_data else None

    #Set category
    category_res = requests.get(f"{WORDPRESS_SITE}categories", auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD))
    category_res.raise_for_status()
    categories = category_res.json()
    category_dict = {cat['name']: cat['id'] for cat in categories}
    
    if blog_data['category'] in category_dict:
        post_data['categories'] = [category_dict[blog_data['category']]]
    else:
        #If category doesn't exist, create it
        new_category_res = requests.post(f"{WORDPRESS_SITE}categories", json={'name': blog_data['category']},
                                         auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD))
        new_category_res.raise_for_status()
        new_category_id = new_category_res.json()['id']
        post_data['categories'] = [new_category_id]

    #Create Gutenberg blocks for the content
    blocks = []

    #Add image block if images are present
    if blog_data['images']:
        first_image_url = blog_data['images'][0]
        image_id = upload_image_to_wordpress(first_image_url)
        if image_id:
            blocks.append({
                "blockName": "core/image",
                "attrs": {
                    "id": image_id, 
                    "url": first_image_url, 
                    "alt": blog_data['title'],  #Using the blog title as alt text for now
                    "align": "center",
                    "sizeSlug": "large",  # WordPress size slug, e.g., "thumbnail", "medium", "large"  # Ensure the image is centered
                },
                "innerBlocks": [],
                "innerHTML": f'<figure class="wp-block-image aligncenter"><img src="{first_image_url}" alt="{blog_data["title"]}" /></figure>'
            })

    # Add the content block (paragraph block for blog content)
    blocks.append({
        "blockName": "core/paragraph",
        "attrs": {},
        "innerBlocks": [],
        "innerHTML": blog_data['content']
    })

    # Convert blocks to Gutenberg-compatible format
    post_data['content'] = serialize_blocks(blocks)

    # Make the API call to create the post
    response = requests.post(f"{WORDPRESS_SITE}posts", json=post_data, auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD))
    
    if response.status_code == 201:
        print(f"Post '{blog_data['title']}' created successfully.")
    else:
        print(f"Failed to create post '{blog_data['title']}': {response.text}")

# Extract content for each blog
for url in blog_urls:
    blog_data = extract_blog_content(url)
    create_post_in_wordpress(blog_data)

# Close the browser
driver.quit()

print("Blog migration complete!")
