import asyncio
import os
from datetime import datetime

from config.config import redis_client, agent_executor
from llm.validate import validating_market
from twitter.client import login, client
from utils.tavily_search import search_util

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

                        # 处理评论
                        if "@" in reply.full_text:
                            result, _ = validating_market(reply.full_text, agent_executor, search_util)
                            if result.get("is_valid", False):
                                # create_bet
                                # bet_created = await create_bet(reply)
                                bet_created = True
                                if bet_created:
                                    try:
                                        await reply.reply("Create Bet Successfully!" + "Url is as below: ")
                                        print(f"Replied to user: {reply.user.screen_name}")
                                    except Exception as e:
                                        print(f"Failed to send reply: {e}")
                                        await asyncio.sleep(10)
                                else:
                                    print("Failed to create bet. Skipping reply.")
                        await asyncio.sleep(1)

                    #     # analyze and process comment
                    #     # response = await analyze_reply_for_transfer(reply.full_text)
                    #     response = None
                    #     # Check if an address and amount are present
                    #     if response:
                    #         to_address = response.get("to_address")
                    #         amount = response.get("amount")
                    #         currency_type = response.get("currency_type")
                    #         reply_content = response.get("reply_content")
                    #
                    #         # transfer the money
                    #         if to_address and amount and currency_type:
                    #             try:
                    #                 amount = int(amount)
                    #                 # Get user_id from the reply
                    #                 to_user_id = reply.user.id
                    #                 user_claim_key = f"user_claimed:{to_user_id}"
                    #
                    #                 # Check if user has already claimed the reward
                    #                 has_claimed = await redis_client.get(user_claim_key)
                    #                 if not has_claimed:
                    #                     print(f"User {to_user_id} has not already claimed the reward.")
                    #                     # # continue
                    #                     # if currency_type == "CKB":
                    #                     #     if CKB_MIN <= amount <= CKB_MAX:
                    #                     #         transfer_result = await transfer_ckb(to_address, amount)
                    #                     # elif currency_type == "Seal":
                    #                     #     if SEAL_MIN <= amount <= SEAL_MAX:
                    #                     #         transfer_result = await transfer_token(to_address, amount, SEAL_XUDT_ARGS)
                    #                     # else:
                    #                     #     print("Unrecognized currency type in response:", currency_type)
                    #                     #     continue
                    #                     # Mark user as claimed in Redis
                    #                     await redis_client.set(user_claim_key, "claimed")
                    #                     # print("Transfer Result:", transfer_result)
                    #             except Exception as e:
                    #                 print(f"Transfer error:{e}")
                    #         if reply_content:
                    #             try:
                    #                 await reply.reply(reply_content)
                    #             except Exception as e:
                    #                 print(f"Failed to send reply, retrying: {e}")
                    #                 await asyncio.sleep(60)  # Delay before retrying
                    #
                    #     await asyncio.sleep(30)
                    #     now_count += 1
                    # if not is_fetch_and_analyze_active:
                    #     return
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

