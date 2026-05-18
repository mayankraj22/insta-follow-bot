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
# FIX 2: Add stealth arguments to browser launch (Line 66)
        browser = p.chromium.launch(headless=True,
           args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ]
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        # Bypass Playwright detection
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
        
        page = context.new_page()
        # page = browser.new_page()
# Begin of changes 
# Increasing the timeout to 60sec to allow for slower connections or Instagram's rate limits
        # page.goto("https://www.instagram.com/accounts/login/")
        # time.sleep(5)
        # page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
        
        # page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
        page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)  # Additional wait for dynamic content
        # page.screenshot(path="debug_login.png")  # Add this
        # print("Page loaded, attempting to find username input...")  # Add this
        # page.wait_for_selector('input[name="username"]', timeout=60000)
# REPLACEMENT START

        page.screenshot(path="login_debug.png")
        print("Loaded URL:", page.url)

        selectors = [
            'input[name="username"]',
            'input[aria-label="Phone number, username, or email"]',
            'input[type="text"]'
        ]

        found = False

        for selector in selectors:
            try:
                page.wait_for_selector(selector, timeout=15000)
                page.fill(selector, USERNAME)
                found = True
                print("Username field found:", selector)
                break
            except:
                continue

        if not found:
            page.screenshot(path="failed_login.png")
            raise Exception("No login field found. Check screenshots in Actions artifacts.")

        page.locator('input[type="password"]').fill(PASSWORD)
        page.locator('button[type="submit"]').click()

# REPLACEMENT END
# FIX 1: Add retry logic (Lines 73-87 replacement)
        # max_retries = 3
        # for attempt in range(max_retries):
        #     try:
        #         page.wait_for_selector('input[name="username"]', timeout=30000)
        #         break
        #     except Exception as e:
        #         print(f"Attempt {attempt + 1} failed: {str(e)}")
        #         if attempt < max_retries - 1:
        #             page.reload()
        #             time.sleep(3)
        #         else:
        #             raise Exception("Failed to load login page after multiple attempts")
# End of changes                 
        # page.fill('input[name="username"]', USERNAME)
        # page.fill('input[name="password"]', PASSWORD)
        # page.click('button[type="submit"]')

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