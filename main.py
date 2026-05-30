# from multiprocessing import context #Commenting 
import os
import json
import time
from playwright.sync_api import sync_playwright

# USERNAME = os.getenv("USERNAME")#For running it locally comment
USERNAME = "username" #For running it locally uncomment
# PASSWORD = os.getenv("PASSWORD")#For running it locally comment
PASSWORD = "password" #For running it locally uncomment

DB_FILE = "followers.json"

MESSAGE = """Hi 👋 Thanks for following.

We are GTM Engineers.

Reply with:
Category
Platform
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

    try:
        page.goto(
            f"https://www.instagram.com/{USERNAME}/",
            wait_until="domcontentloaded",
            timeout=90000
        )

    except:
        print("Profile navigation interrupted, retrying...")
        time.sleep(10)

        page.goto(
            f"https://www.instagram.com/{USERNAME}/",
            wait_until="domcontentloaded",
            timeout=90000
        )

    time.sleep(8)

    # page.screenshot(path="profile_loaded.png") #For debugging purpose

    follower_selectors = [
        f'a[href="/{USERNAME}/followers/"]',
        f'a[href="/{USERNAME}/follower/"]',
        'a[href$="/followers/"]',
        'a[href$="/follower/"]',
        'text=followers',
        'text=follower',
        'text=Followers',
        'text=Follower'
    ]

    opened = False

    for selector in follower_selectors:

        try:
            locator = page.locator(selector).first

            locator.wait_for(state="visible", timeout=5000)

            locator.click(force=True)

            page.wait_for_selector('div[role="dialog"]', timeout=10000)

            print("Followers popup opened using:", selector)
            
            page.mouse.wheel(0, 2000)
            time.sleep(3)
            opened = True
            break

        except:
            continue

    if not opened:

        # page.screenshot(path="followers_fail.png") #For debugging purpose

        input(
            "Followers popup not opened. Open manually then press Enter..."
        )

    time.sleep(5)

    popup = page.locator('div[role="dialog"]').last

    followers = set()

    for scroll_round in range(10):

        print(f"SCROLL ROUND: {scroll_round}")

        # FIXED HERE
        # rows = popup.locator("li").all()

        # print("TOTAL ROWS FOUND:", len(rows))

        # Instagram changed structure
        # capture all visible row containers instead of li

        rows = popup.locator('div[style*="flex-direction: column"]').all() #Commenting temporary it was working previously but instagram changed the structure again
        # rows = popup.locator("li").all()#li never works in identifying the followers list as instagram changed the structure again, using div with flex direction column as fallback which seems to be working for now

        # fallback
        if len(rows) == 0:
            # rows = popup.locator('div[role="button"]').all() #Commenting temporary it was working previously but instagram changed the structure again
            rows = popup.locator('div[role="dialog"] div').all()

        print("TOTAL ROWS FOUND:", len(rows))

        for row in rows:
            
            try:

                row_text = row.inner_text().lower()

                if len(row_text.strip()) == 0:
                    continue

                print("ROW TEXT:", row_text[:200])

                # REAL FOLLOWERS ONLY
                # if "remove" not in row_text:
                #     continue

                # reject suggestions
                if "suggested for you" in row_text:
                    continue

                profile_links = row.locator('a[href^="/"]').all()

                print("LINKS FOUND:", len(profile_links))

                for profile in profile_links:

                    href = profile.get_attribute("href")

                    print("RAW HREF:", href)

                    if not href:
                        continue

                    clean_user = href.strip("/").lower()

                    # skip nested paths
                    if "/" in clean_user:
                        continue

                    blocked = [
                        USERNAME.lower(),
                        "explore",
                        "accounts",
                        "reels",
                        "direct",
                        "stories",
                        "p"
                    ]

                    if clean_user in blocked:
                        continue

                    # valid instagram username only
                    if len(clean_user) < 2:
                        continue

                    followers.add(clean_user)

                    print("FOLLOWER ADDED:", clean_user)

                    break

            except Exception as e:

                print("ROW FAILED:", e)

        # scroll popup
        popup.evaluate("(el) => el.scrollBy(0, 1500)")

        time.sleep(3)

    print("FINAL FOLLOWERS:", followers)

    if len(followers) == 0:

        print("No followers found. Skipping DM process.")
        return []

    return list(followers)

def send_dm(page, username):

#----------Begin of Changes--------#

    try:

        print(f"Opening profile: {username}")

        # --------------------------------
        # OPEN PROFILE
        # --------------------------------

        page.goto(
            f"https://www.instagram.com/{username}/",
            wait_until="domcontentloaded",
            timeout=90000
        )

        time.sleep(5)

        # reduce zoom for better UI visibility
        page.evaluate("document.body.style.zoom='70%'")

        # page.screenshot(path="profile_opened.png") #For debugging purpose

        # --------------------------------
        # CLICK MESSAGE BUTTON
        # --------------------------------

        clicked = False

        message_buttons = [

            'div[role="button"]:has-text("Message")',

            'text=Message'
        ]

        for btn in message_buttons:

            try:

                button = page.locator(btn).first

                button.wait_for(timeout=10000)

                button.click(force=True)

                print("Message button clicked")

                clicked = True

                break

            except Exception as e:

                print("MESSAGE BUTTON FAILED:", btn, e)

        if not clicked:

            print("Message button not found")
            return

        time.sleep(5)

        # page.screenshot(path="message_sidebar.png") #For debugging purpose

        # --------------------------------
        # CLICK NEW MESSAGE BUTTON
        # --------------------------------

        new_message_clicked = False

        new_message_selectors = [

            'svg[aria-label="New message"]',

            'div[role="button"]:has(svg[aria-label="New message"])',

            'text="New message"'
        ]

        for selector in new_message_selectors:

            try:

                print("TRYING NEW MESSAGE:", selector)

                btn = page.locator(selector).first

                btn.wait_for(timeout=5000)

                btn.click(force=True)

                new_message_clicked = True

                print("New message clicked")

                break

            except Exception as e:

                print("NEW MESSAGE FAILED:", selector, e)

        if not new_message_clicked:

            # page.screenshot(path="new_message_fail.png") #For debugging purpose

            print("Could not click new message")
            return

        time.sleep(4)

        # page.screenshot(path="new_message_popup.png") #For debugging purpose

        # --------------------------------
        # SEARCH USERNAME
        # --------------------------------

        search_selectors = [

            'input[placeholder*="Search"]',

            'input[name="queryBox"]',

            'input[type="text"]'
        ]

        search_found = False

        for selector in search_selectors:

            try:

                print("TRYING SEARCH:", selector)

                search_box = page.locator(selector).last

                search_box.wait_for(timeout=10000)

                search_box.click(force=True)

                time.sleep(1)

                search_box.fill(username)

                print("USERNAME TYPED")

                search_found = True

                break

            except Exception as e:

                print("SEARCH FAILED:", selector, e)

        if not search_found:

            # page.screenshot(path="search_fail.png") #For debugging purpose

            print("Search box not found")
            return

        time.sleep(5)

        # page.screenshot(path="username_search_result.png") #For debugging purpose

        # --------------------------------
        # SELECT USER CORRECTLY
        # --------------------------------

        selected = False

        try:

            # wait for search result to appear
            time.sleep(6)

            # page.screenshot(path="before_user_selection.png") #For debugging purpose

            # locate all visible rows
            rows = page.locator('div[role="button"]')

            total = rows.count()

            print("TOTAL BUTTON ROWS:", total)

            for i in range(total):

                try:

                    row = rows.nth(i)

                    text = row.inner_text().lower()

                    print("ROW:", text[:200])

                    # target exact username row
                    if username.lower() in text:

                        row.scroll_into_view_if_needed()

                        time.sleep(1)

                        row.click(force=True)

                        selected = True

                        print("USERNAME ROW CLICKED")

                        break

                except Exception as e:

                    print("ROW FAILED:", e)

            # fallback
            if not selected:

                try:

                    print("TRYING TEXT FALLBACK")

                    text_locator = page.get_by_text(username, exact=False).last

                    text_locator.wait_for(timeout=5000)

                    text_locator.click(force=True)

                    selected = True

                    print("TEXT FALLBACK CLICKED")

                except Exception as e:

                    print("TEXT FALLBACK FAILED:", e)

            if not selected:

                # page.screenshot(path="user_select_fail.png") #For debugging purpose

                print("Could not select user")

                return

        except Exception as e:

            print("USER SELECT FAILED:", e)

            # page.screenshot(path="user_select_exception.png") #For debugging purpose

            return
        
        # --------------------------------
        # CLICK CHAT BUTTON
        # --------------------------------

        chat_clicked = False

        chat_selectors = [

            'div[role="button"]:has-text("Chat")',

            'text=Chat'
        ]

        for selector in chat_selectors:

            try:

                print("TRYING CHAT BUTTON:", selector)

                chat_btn = page.locator(selector).last

                chat_btn.wait_for(timeout=10000)

                chat_btn.click(force=True)

                chat_clicked = True

                print("Chat button clicked")

                break

            except Exception as e:

                print("CHAT BUTTON FAILED:", selector, e)

        if not chat_clicked:

            # page.screenshot(path="chat_button_fail.png") #For debugging purpose

            return

        time.sleep(6)

        # page.screenshot(path="chat_opened.png") #For debugging purpose

        # --------------------------------
        # FIND MESSAGE INPUT
        # --------------------------------

        typed = False

        time.sleep(5)

        # page.screenshot(path="before_typing.png") #For debugging purpose

        message_selectors = [

            'div[contenteditable="true"][role="textbox"]',

            'div[aria-label="Message"]',

            'div[role="textbox"]',

            'textarea',

            'p'
        ]

        for selector in message_selectors:

            try:

                print("TRYING MESSAGE BOX:", selector)

                boxes = page.locator(selector)

                count = boxes.count()

                print("BOX COUNT:", count)

                if count == 0:
                    continue

                box = boxes.last

                box.wait_for(timeout=10000)

                box.click(force=True)

                time.sleep(2)

                page.keyboard.press("Control+A")
                time.sleep(1)

                page.keyboard.type(
                    MESSAGE,
                    delay=40
                )

                typed = True

                print("MESSAGE TYPED")

                break

            except Exception as e:

                print("MESSAGE BOX FAILED:", selector, e)

        if not typed:

            # page.screenshot(path="message_box_fail.png") #For debugging purpose

            print("Message input not found")

            return

        time.sleep(2)

        # --------------------------------
        # SEND MESSAGE
        # --------------------------------

        send_clicked = False

        send_selectors = [

            'div[role="button"]:has-text("Send")',

            'text=Send'
        ]

        for selector in send_selectors:

            try:

                send_btn = page.locator(selector).last

                send_btn.wait_for(timeout=5000)

                send_btn.click(force=True)

                send_clicked = True

                print("SEND BUTTON CLICKED")

                break

            except:
                pass

        # fallback
        if not send_clicked:

            page.keyboard.press("Enter")

            print("ENTER PRESSED TO SEND")

        print("DM SENT TO:", username)

        time.sleep(5)

    except Exception as e:

        print("DM FAILED:", username, e)
#----------End of Changes--------#    

def main():
    known = load_db()

    with sync_playwright() as p:
        #---------Begin of Changes--------#
        #Commenting below code to fix login issue and adding manual step to complete login
        # browser = p.chromium.launch(
        #     headless=False,  # For local testing
        #     slow_mo=500,
        #     args=[
        #         "--disable-blink-features=AutomationControlled",
        #         "--disable-dev-shm-usage",
        #         "--no-sandbox",
        #     ]
        # )
        #Replacing above code with below to fix login issue and adding manual step to complete login
        USER_DATA_DIR = "ig_user_data"

        context = p.chromium.launch_persistent_context(
        USER_DATA_DIR,
        headless=False,
        slow_mo=1000,
        viewport={"width": 1024, "height": 700},
        args=[
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        ]
        )

        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => false})"
        )

        # Reuse existing tab if available
        if len(context.pages) > 0:
            page = context.pages[0]
        else:
            page = context.new_page()

        page.goto(f"https://www.instagram.com/{USERNAME}/",
        wait_until="domcontentloaded",
        timeout=90000)
        time.sleep(8)

        print("Current URL after startup:", page.url)

        # check if already logged in
        logged_in = False

        try:
            page.locator('svg[aria-label="Home"]').first.wait_for(timeout=5000)
            logged_in = True
            print("Existing login session detected")

        except:
            print("No valid session found")

        # if still redirected to login then do login flow
        # if "accounts/login" in page.url:
        if not logged_in:
            try:
                page.goto("https://www.instagram.com/accounts/login/",wait_until="domcontentloaded",
                timeout=90000)
                time.sleep(8)
            except:
                print("Instagram load timeout, continuing anyway...")    

            print("Current URL:", page.url)
            print("\n==============================")
            print("MANUAL LOGIN REQUIRED")
            print("1. Enter username")
            print("2. Enter password")
            print("3. Complete OTP")
            print("4. Click 'Save Login Info'")
            print("5. Reach Instagram Home Feed")
            print("==============================\n")

            input("After login is completely finished, press Enter...")

            print("Waiting for successful login...")

            logged_in = False

            for _ in range(90):

                time.sleep(2)

                current = page.url
                print("Checking:", current)

                try:
                    # check for Instagram home/profile UI
                    page.locator('a[href="/direct/inbox/"]').first.wait_for(timeout=5000)

                    logged_in = True
                    print("Login success detected")
                    break

                except:
                    pass

                try:
                    # alternate check: DM icon exists
                    page.locator('a[href="/direct/inbox/"]').first.wait_for(timeout=3000)

                    logged_in = True
                    print("Login success detected")
                    break

                except:
                    pass

                print("Waiting for OTP/manual verification...")

            if not logged_in:

                # page.screenshot(path="login_failed.png") #For debugging purpose
                raise Exception("Login failed after waiting")
            # # wait for Instagram to fully stabilize after login
        

        print("Waiting before follower scraping...")
        time.sleep(15)
        followers = scrape_followers(page)
        print("Fetched followers:", followers)
        new_users = set(followers) - known

        for user in new_users:
            send_dm(page, user)


        # overwrite DB with latest followers list
        save_db(set(followers))

        # browser.close()#Temporary commenting to keep the browser open for debugging
        #---------Begin of Changes--------#
        # input("Press Enter to close browser...")
        print("Saving browser profile...")
        time.sleep(10)

        context.close()

        print("Session saved successfully")

        #---------End of Changes--------#

if __name__ == "__main__":
    main()