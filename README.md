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
# Instagram Auto DM Bot (Playwright + Python)

## Overview

This project automatically:

1. Logs into Instagram using a persistent browser profile.
2. Detects new followers of a business account.
3. Stores previously processed followers.
4. Sends a predefined DM only to newly detected followers.
5. Prevents duplicate DMs by maintaining a local database.

The solution uses:

* Python
* Playwright
* Persistent Browser Profile (`ig_user_data`)
* Instagram Web Interface

---

# Features

1 Persistent login using Playwright user profile

2 One-time manual login

3 Automatic session reuse

4 Automatic follower scraping

5 Detects only new followers

6 Sends welcome DM automatically

7 Prevents duplicate messaging

8 Handles Instagram UI changes with fallback selectors

9 Local storage using JSON
---

# Project Structure

```text
insta-follow-bot/
│
├── main.py
├── followers.json
├── ig_user_data/
├── requirements.txt
└── README.md
```

### File Description

| File             | Purpose                        |
| ---------------- | ------------------------------ |
| main.py          | Main automation script         |
| followers.json   | Stores processed followers     |
| ig_user_data     | Stores Instagram login session |
| requirements.txt | Python dependencies            |
| README.md        | Project documentation          |

---

# Installation

## Clone Repository

```bash
git clone <your-repository-url>
cd insta-follow-bot
```

---

## Create Virtual Environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Install Playwright Browsers

```bash
playwright install
```

---

# Configuration

Update these variables in `main.py`

```python
USERNAME = "your_instagram_username"
PASSWORD = "your_password"
```

Update the welcome message:

```python
MESSAGE = """
Hi 👋 Thanks for following.

We are GTM Engineers.

Reply with:
Category
Platform
"""
```

---

# First Time Setup (Manual Login)

The first run requires manual login.

Delete any existing profile if needed:

```text
ig_user_data/
```

Then run:

```bash
python main.py
```

The script will display:

```text
MANUAL LOGIN REQUIRED

1. Enter username
2. Enter password
3. Complete OTP
4. Click Save Login Info
5. Reach Instagram Home Feed
```

Complete the login manually inside the opened browser.

After reaching the Instagram home page:

```text
Press Enter...
```

The script will verify login and save the browser session.

---

# Session Persistence

The project uses:

```python
launch_persistent_context()
```

with:

```python
USER_DATA_DIR = "ig_user_data"
```

This stores:

* Cookies
* Local Storage
* Login Session
* Device Trust Information

inside:

```text
ig_user_data/
```

Future executions reuse this session.

No OTP is required unless Instagram invalidates the session.

---

# How It Works

## Step 1

Open Instagram profile

```text
https://www.instagram.com/<username>/
```

---

## Step 2

Open Followers Popup

The bot locates the followers button using multiple fallback selectors.

---

## Step 3

Scrape Followers

The popup is scrolled multiple times.

The bot extracts usernames from profile links.

Example:

```text
/john_doe/
```

becomes

```text
john_doe
```

---

## Step 4

Remove Invalid Entries

Ignored entries:

```text
explore
accounts
reels
stories
direct
```

Also ignores:

```text
Suggested for you
```

recommendations.

---

## Step 5

Compare Against Database

Existing users:

```json
[
  "user1",
  "user2"
]
```

are loaded from:

```text
followers.json
```

New followers are calculated as:

```python
new_users = set(followers) - known
```

---

## Step 6

Send DM

For every new follower:

1. Open profile
2. Click Message
3. Open New Message dialog
4. Search username
5. Select user
6. Click Chat
7. Type message
8. Send message

---

## Database

Processed followers are stored in:

```text
followers.json
```

Example:

```json
[
  "john_doe",
  "jane_smith",
  "creator123"
]
```

This prevents sending duplicate DMs.

---

# Running the Bot

```bash
python main.py
```

Typical output:

```text
Existing login session detected

Followers popup opened

FINAL FOLLOWERS:
{'user1', 'user2'}

Fetched followers:
['user1', 'user2']

DM SENT TO:
user1
```

---

# Reset Login Session

If Instagram logs out unexpectedly:

1. Close the bot
2. Delete:

```text
ig_user_data/
```

3. Run:

```bash
python main.py
```

4. Perform manual login again

A fresh session will be saved.

---

# Common Issues

## Login Page Keeps Loading

Possible causes:

* Instagram temporary rate limiting
* VPN usage
* Network issues
* Corrupted browser profile

Fix:

```text
Delete ig_user_data
```

and perform manual login again.

---

## OTP Appears Again

Instagram may invalidate sessions when:

* Password changes
* Suspicious login activity
* New device detection
* Cookie expiration

Fix:

```text
Delete ig_user_data
```

and login again.

---

## Followers Not Detected

Instagram frequently changes DOM structure.

Current implementation includes multiple fallback selectors, but future updates may require selector adjustments.

---

## DM Not Sent

Possible causes:

* User disabled DMs
* Instagram restrictions
* Selector changes
* Temporary rate limits

Check terminal logs for the failed step.

---

# Important Notes

* Use responsibly.
* Excessive DMs may trigger Instagram anti-spam systems.
* Avoid sending large volumes in a short time.
* Keep delays between actions.
* Monitor account health regularly.

---

# Future Improvements

* Cloud deployment
* Scheduled execution
* Multi-account support
* CSV logging
* SQLite database
* AI-generated personalized messages
* Automatic retry logic
* Docker support
* GitHub Actions support

---

# Tech Stack

* Python
* Playwright
* Chromium
* JSON Storage
* Instagram Web

---

# License

This project is intended for educational and personal automation purposes.

Use at your own risk and comply with Instagram Terms of Service.

---

# For Final Production

To make the solution production-ready, the automation can be deployed on a VPS or cloud server where it runs 24/7 without requiring a personal laptop. 

The setup involves hosting the Python + Playwright application on a Windows VPS or cloud VM, performing a one-time manual Instagram login, and securely storing the authenticated browser profile in a persistent ig_user_data directory. 

Once the session is established, the bot automatically reuses the saved login, periodically checks for new followers, compares them against a local follower database, and sends personalized welcome DMs only to new users. 

By scheduling the script through Task Scheduler (Windows) or Cron Jobs (Linux), the entire workflow becomes fully autonomous. 

This architecture separates the automation from local hardware, provides continuous uptime, enables remote monitoring, and lays the foundation for future enhancements such as dashboards, analytics, multi-account support, and SaaS-style scaling. 

In essence, moving the bot to a cloud environment transforms it from a proof-of-concept script into a reliable, always-on customer engagement system capable of operating at production scale.
