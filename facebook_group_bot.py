from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Facebook credentials and group URL
facebook_email = "03098719135"  # Replace with your email
facebook_password = "zaighum987"  # Replace with your password
group_url = "https://www.facebook.com/groups/44275187995/members"  # Replace with your group URL

# Initialize WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Optional: Start maximized
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open Facebook login page
driver.get("https://www.facebook.com/login")

# Log in to Facebook
email_input = driver.find_element(By.ID, "email")
email_input.send_keys(facebook_email)
password_input = driver.find_element(By.ID, "pass")
password_input.send_keys(facebook_password)
password_input.send_keys(Keys.RETURN)

# Wait for login to complete
time.sleep(5)  # Adjust sleep time if necessary

# Go to the specified group link
driver.get(group_url)

# Wait to load the group page
time.sleep(5)  # Adjust sleep time based on page load time

# Scroll to the bottom of the page to load more members
scroll_pause_time = 3  # Pause time between scrolls
last_height = driver.execute_script("return document.body.scrollHeight")

# Loop to keep scrolling and loading more members
while True:
    # Scroll down
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    
    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# List to store scraped member data
members_data = []

# Scrape member names and profile links
member_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'profile.php?id=') or contains(@href, '/user/')]")
for member in member_elements:
    member_name = member.text
    member_link = member.get_attribute('href')
    if member_name and member_link:
        members_data.append([member_name, member_link])

# Save scraped data to a CSV file
csv_file = "facebook_group_members.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Profile Link"])
    writer.writerows(members_data)

print(f"Scraped {len(members_data)} members. Data saved to {csv_file}")

# Optional: Close the browser
driver.quit()
