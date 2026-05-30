# from multiprocessing import context #Commenting 
import os
import json
import time
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("USERNAME")#For running it locally comment
# USERNAME = "username_here" #For running it locally uncomment
PASSWORD = os.getenv("PASSWORD")#For running it locally comment
# PASSWORD = "password_here" #For running it locally uncomment

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

    page.screenshot(path="profile_loaded.png")

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

        page.screenshot(path="followers_fail.png")

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

    # try:

    #     print(f"Opening profile: {username}")

    #     page.goto(
    #         f"https://www.instagram.com/{username}/",
    #         wait_until="domcontentloaded",
    #         timeout=90000
    #     )

    #     time.sleep(10)

    #     # --------------------------------
    #     # CLICK MESSAGE BUTTON
    #     # --------------------------------

    #     clicked = False

    #     message_buttons = [

    #         'div[role="button"]:has-text("Message")',

    #         'text=Message'
    #     ]

    #     for btn in message_buttons:

    #         try:

    #             button = page.locator(btn).first

    #             if button.is_visible(timeout=5000):

    #                 button.click(force=True)

    #                 clicked = True

    #                 print("Message button clicked")

    #                 break

    #         except Exception as e:

    #             print("MESSAGE BUTTON FAILED:", btn, e)

    #     if not clicked:

    #         print("Message button not found:", username)
    #         return

    #     # WAIT FOR CHAT THREAD TO LOAD
    #     time.sleep(12)

    #     # --------------------------------
    #     # HANDLE OPTIONAL POPUPS
    #     # --------------------------------

    #     popup_buttons = [
    #         'text=Not Now',
    #         'text=Cancel',
    #         'text=Close',
    #         'text=Continue'
    #     ]

    #     for popup in popup_buttons:

    #         try:

    #             page.locator(popup).first.click(timeout=2000)

    #             print("Popup handled:", popup)

    #             time.sleep(1)

    #         except:
    #             pass

    #     # DEBUG
    #     page.screenshot(path="after_message_click.png")

    #     # --------------------------------
    #     # FIND ACTUAL MESSAGE BOX
    #     # --------------------------------

    #     typed = False

    #     selectors = [

    #         'div[contenteditable="true"]',

    #         'div[role="textbox"]',

    #         'textarea'
    #     ]

    #     for selector in selectors:

    #         try:

    #             print("TRYING:", selector)

    #             box = page.locator(selector).last

    #             box.wait_for(
    #                 state="visible",
    #                 timeout=15000
    #             )

    #             box.click(force=True)

    #             time.sleep(2)

    #             # use keyboard typing only
    #             page.keyboard.type(
    #                 MESSAGE,
    #                 delay=25
    #             )

    #             typed = True

    #             print("MESSAGE TYPED")

    #             break

    #         except Exception as e:

    #             print("SELECTOR FAILED:", selector, e)

    #     if not typed:

    #         page.screenshot(path="dm_box_fail.png")

    #         print("Message input not found")

    #         return

    #     time.sleep(2)

    #     # --------------------------------
    #     # SEND MESSAGE
    #     # --------------------------------

    #     page.keyboard.press("Enter")

    #     print("DM SENT:", username)

    #     time.sleep(5)

    # except Exception as e:

    #     print("DM FAILED:", username, e)
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

        page.screenshot(path="profile_opened.png")

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

        page.screenshot(path="message_sidebar.png")

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

            page.screenshot(path="new_message_fail.png")

            print("Could not click new message")
            return

        time.sleep(4)

        page.screenshot(path="new_message_popup.png")

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

            page.screenshot(path="search_fail.png")

            print("Search box not found")
            return

        time.sleep(5)

        page.screenshot(path="username_search_result.png")

        # --------------------------------
        # SELECT USER CORRECTLY
        # --------------------------------

        selected = False

        try:

            # wait for search result to appear
            time.sleep(6)

            page.screenshot(path="before_user_selection.png")

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

                page.screenshot(path="user_select_fail.png")

                print("Could not select user")

                return

        except Exception as e:

            print("USER SELECT FAILED:", e)

            page.screenshot(path="user_select_exception.png")

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

            page.screenshot(path="chat_button_fail.png")

            return

        time.sleep(6)

        page.screenshot(path="chat_opened.png")

        # --------------------------------
        # FIND MESSAGE INPUT
        # --------------------------------

        typed = False

        time.sleep(5)

        page.screenshot(path="before_typing.png")

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

            page.screenshot(path="message_box_fail.png")

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

        # browser = context.browser
        #---------End of Changes--------#
        #---------Begin of Changes--------#
        #Commenting below code to fix login issue and adding manual step to complete login
        # SESSION_FILE = "session.json"

        # if os.path.exists(SESSION_FILE):
        #     print("Using saved session")
        #     context = browser.new_context(
        #         storage_state=SESSION_FILE,
        #         viewport={"width": 1366, "height": 768}
        #     )
        # else:
        #     print("No session found. First login.")
        #     context = browser.new_context(
        #         viewport={"width": 1366, "height": 768}
        #     )
        #---------End of Changes--------#
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => false})"
        )

        # page = context.new_page()
        # Reuse existing tab if available
        if len(context.pages) > 0:
            page = context.pages[0]
        else:
            page = context.new_page()
        # page = browser.new_page()

        # page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
        # page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded", timeout=30000)
        # time.sleep(5)
        # page.screenshot(path="debug_login.png")
        # print("Page loaded, attempting to find username input...")
        # page.wait_for_selector('input[name=\"username\"]', timeout=60000)

        # if os.path.exists(SESSION_FILE):#replacing with below code to fix login issue and adding manual step to complete login
        # if os.path.exists("ig_user_data"):
        #     page.goto("https://www.instagram.com/")
        #     time.sleep(8)

        # else:
        # page.goto("https://www.instagram.com/")
        # time.sleep(8)
        # print("Current URL after startup:", page.url)
        # page.screenshot(path="startup_state.png")
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
            page.screenshot(path="local_debug.png")

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
                raise Exception("Login field not found")

            page.locator('input[type="password"]').fill(PASSWORD)
            # page.locator('button[type="submit"]').click()#commenting to fix loggin issue
            #------Begin of Changes--------#
            login_selectors = [
                'button[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Log In")',
                'div[role="button"]:has-text("Log in")'
            ]

            clicked = False

            for btn in login_selectors:
                try:
                    page.locator(btn).first.wait_for(timeout=5000)
                    page.locator(btn).first.click()
                    print("Clicked login using:", btn)
                    clicked = True
                    break
                except:
                    continue

            if not clicked:
                page.screenshot(path="login_button_fail.png")
                input("Login button not auto-clicked. Press Enter after clicking manually...")
    #---------End of Changes--------#
    #---------Begin of Changes--------#
    #Commenting below code to fix login issue and adding manual step to complete login
            # print("Complete OTP manually if prompted...")
            # time.sleep(30)

            # context.storage_state(path=SESSION_FILE)
            # print("Session saved")
    #----------------------------------------
            print("Waiting for successful login...")

            logged_in = False

            for _ in range(90):

                time.sleep(2)

                current = page.url
                print("Checking:", current)

                try:
                    # check for Instagram home/profile UI
                    # page.wait_for_load_state("networkidle", timeout=5000)
                    # page.locator('svg[aria-label="Home"]').first.wait_for(timeout=3000)
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

                page.screenshot(path="login_failed.png")
                raise Exception("Login failed after waiting")
            # # wait for Instagram to fully stabilize after login
            # time.sleep(10)

            # # ensure homepage fully loaded
            # page.goto("https://www.instagram.com/")
            # time.sleep(5)

            # print("Instagram fully loaded after login")
    #---------End of Changes--------#        

        print("Waiting before follower scraping...")
        time.sleep(15)
        followers = scrape_followers(page)
        print("Fetched followers:", followers)
        new_users = set(followers) - known

        for user in new_users:
            send_dm(page, user)

        # known.update(new_users)
        # save_db(known)
        # overwrite DB with latest followers list
        save_db(set(followers))

        # browser.close()#Temporary commenting to keep the browser open for debugging
        #---------Begin of Changes--------#
        input("Press Enter to close browser...")
        # wait few seconds before closing so session fully persists
        # time.sleep(5)
        # context.close()
        #---------End of Changes--------#

if __name__ == "__main__":
    main()