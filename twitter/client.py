import asyncio
import json
import os
from datetime import datetime, timedelta

from config.config import cookies_path, twitter_cookies, twitter_email, twitter_username, twitter_password, \
    agent_executor
from twikit import Client

from llm.validate import validating_market
from utils.tavily_search import search_util

client = Client('en-US',
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15')


def contains_mention(message: str) -> bool:
    """Check if the message contains an @ mention."""
    return "@" in message


async def validate_market(description: str) -> bool:
    """Wrapper for `validating_market` to validate the market description."""
    analysis_result, _ = validating_market(description, agent_executor, search_util)
    return analysis_result.get("is_valid", False)


async def login():
    print(cookies_path)
    if os.path.exists(cookies_path) and os.path.getsize(cookies_path) > 0:
        print(cookies_path)
        client.load_cookies(cookies_path)
    elif twitter_cookies is not None and twitter_cookies != "":
        cookies = json.loads(twitter_cookies)
        client.set_cookies(cookies)
    else:
        await client.login(auth_info_1=twitter_email, auth_info_2=twitter_username, password=twitter_password)
        client.save_cookies(cookies_path)


async def process_notifications(notifications, time_window=240):
    now = datetime.now()

    # Iterate through the notifications and process them
    for notification in notifications:
        # if notification.tweet:
        #     print(notification.tweet.text)
        # Process only new notifications
        notification_time = datetime.fromtimestamp(notification.timestamp_ms / 1000)
        print(f"notification_time: {notification_time}")
        print(f"stop_time: {now - timedelta(minutes=time_window)}")
        if notification_time < now - timedelta(minutes=time_window):  # Adjust time window
            print("Notification is outside the time window. Skipping.")
            continue
        print(notification.message)
        if notification.tweet:
            print(notification.tweet.text)
            # Check if the message contains an @ mention
            if contains_mention(notification.tweet.text):
                description = notification.tweet.text
                print(f"Processing notification: {description}")

                # Validate the bet
                is_valid = await validate_market(description)
                if is_valid:
                    # await notification.tweet.reply(description)
                    print(notification.tweet.text)
                    # # Create the bet
                    # bet = await create_bet(description)
                    print("Bet created")

                    # Reply to the user that the bet has been created
                    content = f"Your bet has been successfully created!"
                    await notification.tweet.reply(content)
                    # await post_tweet(content)
                else:
                    print("Bet validation failed. No action taken.")

        print(notification)

        # Check for additional pages of notifications
    if await notifications.next():
        print("Fetching next batch of notifications...")
        await process_notifications(await notifications.next(), time_window)


async def fetch_notifications():
    """Fetch and process all notifications."""
    await login()

    # Retrieve initial batch of notifications
    notifications = await client.get_notifications('All')
    print(notifications)
    await process_notifications(notifications)


if __name__ == '__main__':
    asyncio.run(fetch_notifications())
