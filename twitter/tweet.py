import asyncio
import os
from datetime import datetime

from CDP.contract import create_bet
from config.config import redis_client, agent_executor
from llm.validate import validating_market
from twitter.client import login, client
from utils.tavily_search import search_util
from utils.time_util import iso_to_timestamp

# Global variable to stop the loop
_fetch_and_validate_stop_event = asyncio.Event()
_is_fetch_and_validate_active = False

# Getter for fetch_and_validate_stop_event
def get_fetch_and_validate_stop_event():
    global _fetch_and_validate_stop_event
    return _fetch_and_validate_stop_event


# Setter for fetch_and_validate_stop_event
def set_fetch_and_validate_stop_event(event: asyncio.Event):
    global _fetch_and_validate_stop_event
    _fetch_and_validate_stop_event = event


# Getter for is_fetch_and_validate_active
def get_is_fetch_and_validate_active():
    global _is_fetch_and_validate_active
    return _is_fetch_and_validate_active


# Setter for is_fetch_and_validate_active
def set_is_fetch_and_validate_active(active: bool):
    global _is_fetch_and_validate_active
    _is_fetch_and_validate_active = active

async def post_tweet(content, image_paths=None):
    await login()  # Ensure login first
    try:
        if image_paths:
            media_ids = [await client.upload_media(path) for path in image_paths]
            await client.create_tweet(text=content, media_ids=media_ids)
        else:
            await client.create_tweet(text=content)
        # print successfully!!!
        print("\n" + "=" * 30)
        print("Tweet sent successfully")
        print("=" * 30 + "\n")
        return True
    except Exception as e:
        print("\n" + "=" * 30)
        print(f"Tweet send failed, please try again later: {e}")
        print("=" * 30 + "\n")
        return False


async def fetch_and_validate_replies(user_id):
    await login()
    # Define an initial timestamp set to a year in the past
    initial_timestamp = datetime.now().timestamp() - 365 * 24 * 60 * 60

    while not _fetch_and_validate_stop_event.is_set():
        if not _is_fetch_and_validate_active:
            print("Transfer environment setting or fetch mode is disabled. Pausing task.")
            await asyncio.sleep(15)  # Wait before rechecking
            return

        try:
            tweets = await client.get_user_tweets(user_id, "Tweets")
            await asyncio.sleep(1)
            for tweet in tweets:
                tweet_id = tweet.id
                print(tweet.text)
                tweet = await client.get_tweet_by_id(tweet_id)
                await asyncio.sleep(1)
                replies_count = tweet.reply_count
                now_count = 0

                last_processed_time = await redis_client.get(f"csb_last_processed_time:{tweet_id}")
                await asyncio.sleep(1)
                if not last_processed_time:
                    last_processed_time = initial_timestamp
                    await redis_client.set(f"csb_last_processed_time:{tweet_id}", last_processed_time)
                    print(initial_timestamp)
                else:
                    last_processed_time = float(last_processed_time)
                    print(last_processed_time)

                replies = tweet.replies
                print(replies)

                while replies:
                    for reply in replies:
                        print(reply.text)
                        if not _is_fetch_and_validate_active:
                            return
                        reply_timestamp = reply.created_at_datetime.timestamp()

                        # Skip replies processed previously
                        if reply_timestamp <= float(last_processed_time):
                            continue

                        print("Reply:", reply.full_text)
                        # extract comment text
                        full_text = reply.full_text

                        # process comments
                        if "@" in full_text:
                            processed_text = " ".join(
                                [word for word in full_text.split() if not word.startswith("@")]
                            )

                            result, _ = validating_market(processed_text, agent_executor, search_util)
                            if result.get("is_valid", False):
                                timestamp = iso_to_timestamp(result.get("due_date"))
                                # create_bet
                                # bet_created = await create_bet(reply)
                                bet_created = True
                                if bet_created:
                                    # create_bet(processed_text, "0x0000000000000000000000000000000000000000", 1, "0x0000000000000000000000000000000000000000", timestamp)

                                    # 开始轮询，直到 reply.reply 成功
                                    while True:
                                        try:
                                            await reply.reply("Create Bet Successfully! Url is as below:")
                                            print(f"Replied to user: {reply.user.screen_name}")
                                            break  # 成功后退出循环
                                        except Exception as e:
                                            print(f"Failed to send reply, retrying in 120 seconds: {e}")
                                            await asyncio.sleep(120)  # 等待 120 秒后重试

                                else:
                                    print("Failed to create bet. Skipping reply.")
                        await asyncio.sleep(1)
                    if replies.next:
                        try:
                            replies = await replies.next()
                            await asyncio.sleep(10)
                        except Exception as e:
                            print(f"replies.next() error: {e} ")
                            break
                    else:
                        break  # if no more, break it
                # Update last processed time
                last_processed_time = datetime.now().timestamp()
                await redis_client.set(f"csb_last_processed_time:{tweet_id}", last_processed_time)
            await asyncio.sleep(20)
        except Exception as e:
            await asyncio.sleep(10)
            print("\n" + "=" * 30)
            print(f"Failed to retrieve replies: {e}")
            print("=" * 30 + "\n")
            continue

