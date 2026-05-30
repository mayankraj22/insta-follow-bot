# insta-follow-bot

Creating bot to enable auto dm feature on follow business account

1. Create business Instagram account (professional).
2. Add USERNAME and PASSWORD under GitHub repository Secrets.
3. Push files.
4. Enable Actions.
5. Test via workflow\_dispatch.
6. Update scrape\_followers selectors after inspecting current Instagram DOM.

\----------------------------Current Issue---------------------------------------------

1. Currently the test version of google chrome is opening and need to make it large to see the button with userid and password written
2. Need to manually click the button ,a otp is sent for verification at gmail

\---------------------------Final------------------------------------------------------
# Instagram Auto DM Bot using Playwright

## Overview

This project automatically sends a welcome Direct Message (DM) to new Instagram followers.

The bot:

* Logs into Instagram using a persistent browser profile
* Scrapes followers from a business account
* Detects newly added followers
* Opens each follower profile
* Navigates through Instagram's messaging UI
* Sends a predefined onboarding message
* Maintains a follower database to avoid reprocessing existing followers

---

## Features

### Persistent Login

Uses Playwright Persistent Context to preserve Instagram sessions.

Benefits:

* No repeated login prompts
* Reduced OTP challenges
* Session survives script restarts

---

### Automatic Follower Scraping

The bot:

1. Opens the target Instagram profile
2. Opens the Followers popup
3. Scrolls through the followers list
4. Extracts usernames
5. Ignores:

   * Suggested accounts
   * Instagram system links
   * Invalid usernames

---

### New Follower Detection

Follower data is stored in:

```text
followers.json
```

Workflow:

1. Read previously known followers
2. Scrape current followers
3. Identify new followers
4. Send DM only to newly detected accounts

---

### Automated DM Flow

For every new follower:

1. Open follower profile
2. Click Message
3. Open New Message drawer
4. Search follower username
5. Select matching search result
6. Click Chat
7. Type onboarding message
8. Send message

---

## Current Message Template

```text
Hi 👋 Thanks for following.

We are onboarding creators.

Reply with:
Category
Platform
Follower count
```

Can be modified using the MESSAGE variable.

---

## Project Structure

```text
project/
│
├── main.py
├── followers.json
├── ig_user_data/ # Gets auto created to sync business acc login info for every DM workflow
├── profile_loaded.png
├── profile_opened.png
├── message_sidebar.png
├── username_search_result.png
├── before_typing.png
│
└── README.md
```

---

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd instagram-auto-dm
```

### 2. Install Dependencies

```bash
pip install playwright
```

### 3. Install Browser

```bash
playwright install chromium
```

---

## Configuration

Update credentials in:

```python
USERNAME = "your_business_account"
PASSWORD = "your_password"
```

Recommended:

```python
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
```

and store secrets as environment variables.

---

## First Login

Run the script:

```bash
python main.py
```

On first run:

1. Instagram login page opens
2. Credentials are filled automatically
3. Complete OTP manually only for first time
4. Session is stored in:

```text
ig_user_data/
```

Subsequent runs reuse the session.

---

## Instagram UI Flow Implemented

Follower Profile

↓

Message

↓

New Message

↓

Search Username

↓

Select User

↓

Chat

↓

Type Message

↓

Send

---

## Playwright Configuration

Current browser configuration:

```python
context = p.chromium.launch_persistent_context(
    "ig_user_data",
    headless=False,
    slow_mo=1000,
    viewport={
        "width": 1366,
        "height": 768
    }
)
```

Additional anti-detection flags:

```python
--disable-blink-features=AutomationControlled
--disable-dev-shm-usage
--no-sandbox
```

---

## Debug Screenshots

The bot automatically captures screenshots during execution.

Examples:

```text
profile_loaded.png
profile_opened.png
message_sidebar.png
new_message_popup.png
username_search_result.png
chat_opened.png
before_typing.png
```

Useful for troubleshooting Instagram UI changes.

---

## Known Instagram Limitations

Instagram frequently changes:

* DOM structure
* Selectors
* Messaging UI
* Follower popup layout

If automation breaks:

1. Review latest screenshots
2. Inspect Instagram DOM
3. Update affected selectors

---

## Best Practices

### Add Random Delays

Example:

```python
import random

time.sleep(random.randint(3, 7))
```

Helps mimic human behavior.

---

### Limit DM Volume

Avoid:

* Sending hundreds of DMs quickly
* Excessive profile visits
* Repetitive actions

Instagram may apply temporary restrictions.

---

### Verify DM Delivery

Consider:

* Detecting sent message bubbles
* Checking Send button state
* Capturing post-send screenshots

---

## Future Enhancements

### Cloud Hosting

Possible deployment options:

* Railway
* Render
* VPS
* AWS EC2
* DigitalOcean

Persistent browser storage is recommended.

---

### Additional Features

* Personalized messages
* Multiple message templates
* Creator qualification forms
* Google Sheets integration
* CRM integration
* Lead tracking dashboard
* DM success reporting
* Retry mechanism

---

## Disclaimer

This project automates interactions with Instagram's web interface using browser automation.

Instagram may change its UI, policies, or rate limits at any time. Use responsibly and monitor account activity to avoid restrictions.

---

## Status

Current Status: Working

Verified Flow:

Login → Follower Scraping → New Follower Detection → DM Navigation → User Selection → Chat Creation → Message Sending


