import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import pymongo

# Setup Selenium WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Base URL
base_url = "https://www.adultdvdempire.com/all-dvds.html?unlimited=0&media=2&page={}"


# List to store all movie details
all_movie_details = []

# Iterate through pages 1 to 100 done...
for page in range(1, 2808):
    url = base_url.format(page)
    driver.get(url)
    
    # Extract the number of movies on the page
    movie_elements = driver.find_elements(By.XPATH, '//*[@class="row grid-list"]/div')
    
    # Extract movie details for each movie on the current page
    for i in range(1, len(movie_elements)):
        try:
            movie_details = {}
            movie_url = driver.find_element(By.XPATH, f'//*[@class="row grid-list"]/div[{i}]/div/div/a').get_attribute('href')
            title = driver.find_element(By.XPATH, f'//*[@class="row grid-list"]/div[{i}]/div/div/a/img').get_attribute('alt').replace(' Boxcover', '')
            poster_path = driver.find_element(By.XPATH, f'//*[@class="row grid-list"]/div[{i}]/div/div/a/img').get_attribute('src')
            
            poster_id_regex = re.search(r'products/\d+/(.*?)m.jpg', poster_path)
            poster_id = poster_id_regex.group(1).strip() if poster_id_regex else None
            movie_details["id"] = poster_id
            
            movie_details["title"] = title
            
            movie_details["poster_path"] = poster_path
            
            movie_details["url"] = movie_url
            
            all_movie_details.append(movie_details)
            print(f"Added Page: {page}, Movie: {i}")
            # Go back to the main page after extracting details
            
        except Exception as e:
            print(f"Failed to extract details for movie {i} on page {page}: {e}")
            continue

# Close the browser
driver.quit()

# Print the result as JSON
print(json.dumps(all_movie_details, indent=4))

# MongoDB connection setup
client = pymongo.MongoClient("mongodb+srv://Lusty:Lusty50861407@lustyflix.de1oulx.mongodb.net/AdultDVDEmpire?retryWrites=true&w=majority&appName=LustyFlix")
db = client['AdultDVDEmpire']
collection = db['discover']
# Insert the movie details into MongoDB
collection.insert_many(all_movie_details)

print("Data inserted into MongoDB successfully.")
