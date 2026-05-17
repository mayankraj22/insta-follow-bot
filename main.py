import os
import json
import time
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

DB_FILE = "followers.json"

MESSAGE = """Hi 👋 Thanks for following.

We are onboarding creators.

Reply with:
Category
Platform
Follower count
"""

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(list(data), f)

def scrape_followers(page):
    page.goto(f"https://www.instagram.com/{USERNAME}/")
    time.sleep(5)

    page.click("a[href$='/followers/']")
    time.sleep(5)

    followers = []

    # Placeholder for scraping logic
    # we’ll fill this next after your first run

    return followers

def send_dm(page, username):
    page.goto(f"https://www.instagram.com/{username}/")
    time.sleep(4)

    try:
        page.click("text=Message")
        time.sleep(3)

        page.fill("textarea", MESSAGE)
        page.keyboard.press("Enter")

        print("Sent:", username)

    except:
        print("Failed:", username)

def main():
    known = load_db()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://www.instagram.com/accounts/login/")
        time.sleep(5)

        page.fill('input[name="username"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.click('button[type="submit"]')

        time.sleep(10)

        followers = scrape_followers(page)
        new_users = set(followers) - known

        for user in new_users:
            send_dm(page, user)

        known.update(new_users)
        save_db(known)

        browser.close()

if __name__ == "__main__":
    main()