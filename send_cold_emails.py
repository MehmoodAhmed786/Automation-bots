# send_cold_emails.py
import csv
import yagmail

SENDER_EMAIL = "youremail@gmail.com"
APP_PASSWORD = "your app pass"

SUBJECT = "Custom Bots to Automate Your Workflow 🚀"

BODY_TEMPLATE = """\
Hi {{name}},

I came across your company and thought you might benefit from automation solutions.

We build custom bots for marketing, outreach, lead gen, scraping, social engagement, and more.

Would you like a free consultation to see what we can automate for your team?

Cheers,  
Hasnain  
Botanex Forge  
"""

def personalize(name):
    return BODY_TEMPLATE.replace("{{name}}", name if name else "there")

def send_emails(csv_file):
    yag = yagmail.SMTP(SENDER_EMAIL, APP_PASSWORD)

    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['name']
            website = row['website']
            recipient = row.get('email', None)  # Add email field manually

            if recipient:
                print(f"Sending email to: {recipient}")
                try:
                    yag.send(to=recipient, subject=SUBJECT, contents=personalize(name))
                    print("[✓] Email sent")
                except Exception as e:
                    print(f"[!] Failed to send to {recipient}: {e}")
            else:
                print(f"[!] No email for {name} ({website})")

if __name__ == "__main__":
    send_emails("clutch_leads.csv")
