import streamlit as st
import subprocess
import sys

# Streamlit UI for user inputs
st.title("Facebook Group Scraper and Messenger")
# Function to install a package
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install selenium and webdriver_manager if not already installed
try:
    import selenium
except ImportError:
    install('selenium')

try:
    import webdriver_manager
except ImportError:
    install('webdriver-manager')

try:
    import selenium
    import webdriver_manager
    print("Selenium and WebDriver Manager are installed successfully!")
except ImportError as e:
    print(f"Error importing module: {e}")

# Input fields for Facebook credentials and group URL
facebook_email = st.text_input("Facebook Email", placeholder="Enter your Facebook email")
facebook_password = st.text_input("Facebook Password", type="password", placeholder="Enter your Facebook password")
group_url = st.text_input("Group URL", placeholder="Enter the Facebook group URL")

# Path to the backend scripts
selenium_script = "facebook_group_bot.py"
playwright_script = "facebook_message.py"

# Buttons to start the scraping and messaging process
if st.button("Start Scraping and Messaging"):
    if facebook_email and facebook_password and group_url:
        # Run the Selenium and Playwright scripts using subprocess
        try:
            # Execute the Selenium script
            st.write("Starting the Selenium scraping process...")
            result_selenium = subprocess.run(
                ["python3", selenium_script, facebook_email, facebook_password, group_url],
                check=True, capture_output=True, text=True
            )
            st.write("Selenium scraping completed successfully.")
            st.text(result_selenium.stdout)

            # Execute the Playwright script
            st.write("Starting the Playwright messaging process...")
            result_playwright = subprocess.run(
                ["python3", playwright_script], 
                check=True, capture_output=True, text=True
            )
            st.write("Playwright messaging completed successfully.")
            st.text(result_playwright.stdout)

        except subprocess.CalledProcessError as e:
            st.error(f"An error occurred: {e}")
            st.error(e.stderr)  # Display any error messages from the scripts

    else:
        st.warning("Please enter all the required information.")
