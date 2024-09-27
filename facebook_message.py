import asyncio
import csv
import random
from playwright.async_api import async_playwright

async def main(facebook_email, facebook_password, csv_file):
    messages = [
        "Hello! I hope you're doing well.",
        "Hi there! Just wanted to reach out and say hi.",
        "Hey! How's everything going?",
        "Greetings! I wanted to connect with you.",
        "Hi! Hope you’re having a great day!"
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) 
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.facebook.com/login")
        await page.fill("#email", facebook_email)
        await page.fill("#pass", facebook_password)
        await page.click("button[name='login']")

        await page.wait_for_selector("div[role='navigation']", timeout=25000)

        members_data = []
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                members_data.append(row['Profile Link'])  

        for member_link in members_data:
            try:
                await page.goto(member_link)  
                await page.wait_for_timeout(10000)  # Adjust sleep time if necessary

                try:
                    await page.get_by_role("button", name="Message").click()
                except:
                    await page.get_by_text("Message").click()

                await page.wait_for_selector("div[contenteditable='true'][data-testid='conversation-compose-box']", timeout=25000)

                message = random.choice(messages)
                await page.get_by_role("paragraph").click()
                await page.get_by_role("textbox", name="Message").fill(message)
                await page.get_by_label("Press Enter to send").click()

                print(f"Sent message to {member_link}: {message}")

                await page.wait_for_timeout(random.uniform(2000, 5000))

            except Exception as e:
                print(f"An error occurred while messaging {member_link}: {e}")

        await browser.close()

# If you want to run this script standalone (not through Streamlit), you can include this:
if __name__ == "__main__":
    # Replace with actual credentials if running directly
    asyncio.run(main("your_email@example.com", "your_password", "facebook_group_members.csv"))
