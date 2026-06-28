from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import csv

chrome_options = Options()
chrome_options.add_argument("--headless")

# Get the category of videos the user wants to scrape
genre = input("Enter which category of videos you want to scrape (e.g., funny, viral):\n")
YOUTUBE_SEARCH_URL = f'https://www.youtube.com/results?search_query={genre}&sp=EgIQAQ%253D%253D'  # YouTube search for Shorts

# CSV file path to store extracted URLs
URL_FILE_PATH = '/home/student/Documents/youtube.csv'

def extract_youtube_urls():
    # Automatically manage chromedriver installation
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(YOUTUBE_SEARCH_URL)
    
    time.sleep(5)  # Allow time for page load

    urls_and_usernames = []
    previous_count = 0  # Track previously found URLs to detect changes

    while True:
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Allow time for new content to load
        
        # Find the video elements (Shorts video links)
        video_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/shorts/')]")
        
        for video in video_elements:
            url = video.get_attribute('href')
            if '/shorts/' in url and url not in [u[0] for u in urls_and_usernames]:  # Avoid duplicates
                start_index = url.find('@') + 1
                end_index = url.find('/shorts/')
                username = url[start_index:end_index]
                
                urls_and_usernames.append((url, username))
        
        # Stop if no new URLs are found after scrolling
        if len(urls_and_usernames) == previous_count:
            print("No new URLs found. Stopping the extraction.")
            break
        
        previous_count = len(urls_and_usernames)  
    
    file_exists = os.path.isfile(URL_FILE_PATH)

    try:
        # Write extracted URLs and usernames to CSV
        with open(URL_FILE_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['YouTube Shorts URLs', 'Username'])  # Write header if file is new
            for url, username in urls_and_usernames:
                writer.writerow([url, username])
        print(f"Extracted and saved {len(urls_and_usernames)} YouTube Shorts URLs and usernames to {URL_FILE_PATH}.")
    except Exception as e:
        print(f"Error writing to file: {str(e)}")
    
    driver.quit()

extract_youtube_urls()
