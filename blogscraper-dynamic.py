from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time

# Set the path to your ChromeDriver executable
chrome_driver_path = 'C:\\Users\\TouKong\\AppData\\Roaming\\Python\\Python311\\site-packages\\chromedriver-win64\\chromedriver.exe'  # Make sure this path points to your chromedriver.exe

# Initialize the WebDriver using the Service class
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Open the target blog page
driver.get("https://hireveterans.com/blog/")

# Wait for the page to load (adjust time if needed)
time.sleep(3)

# List to store all blog URLs
blog_urls = []

# Function to scroll and click 'Load More' until all posts are loaded
def load_all_blogs():
    while True:
        # Find all blog post links
        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/blog/')]")
        
        # Extract URLs and add to list
        for link in links:
            href = link.get_attribute('href')
            if href not in blog_urls and href.startswith('https://hireveterans.com/blog/') and href != 'https://hireveterans.com/blog/':
                blog_urls.append(href)
        
        try:
            # Find and click the 'Load More' button
            load_more_button = driver.find_element(By.XPATH, "//button[contains(@class, 'load-more')]")
            load_more_button.click()
            
            # Wait for more content to load (adjust time if needed)
            time.sleep(3)
        except Exception as e:
            print("No more 'Load More' button found or error encountered:", e)
            break

# Call the function to load all blogs
load_all_blogs()

# Close the browser
driver.quit()

# Print all collected blog URLs
print("Collected blog URLs:")
for idx, url in enumerate(blog_urls, start=1):
    print(f"{idx}: {url}")