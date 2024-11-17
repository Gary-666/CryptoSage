# main.py

import re
from datetime import datetime

from dateutil.parser import parse

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from CDP.contract import set_bet_result
from config.config import agent_executor
from llm.feedback import collect_feedback_and_improve
from llm.introduce import generate_self_intro_tweet
from llm.validate import validating_market
from twitter.tweet import fetch_and_validate_replies, get_is_fetch_and_validate_active, \
    set_is_fetch_and_validate_active, get_fetch_and_validate_stop_event, post_tweet
from utils.tavily_search import search_util
# FastAPI application
app = FastAPI()

# Request data model
class BetRequest(BaseModel):
    description: str  # Bet description (e.g., weather in Bangkok tomorrow)
    urls: list = []  # Optional list of data source URLs for LLM to query
    address: str

#  Request model for validate_market API
class ValidateMarketRequest(BaseModel):
    description: str  # Market description as input


class FetchAndAnalyzeRepliesRequest(BaseModel):
    user_id: str


class PostTweetRequest(BaseModel):
    address: str
    message: str

class FeedbackRequest(BaseModel):
    message_json: str

# Helper function to parse and standardize the due date
def parse_due_date(due_date_str: str) -> datetime:
    """
    Parse and standardize a due date string into a datetime object.

    Args:
        due_date_str (str): Raw due date string.

    Returns:
        datetime: Parsed and standardized datetime object.
    """
    try:
        parsed_date = parse(due_date_str, fuzzy=True)
        return parsed_date
    except Exception as e:
        print(f"Error parsing due date: {e}")
        return None


# URL extraction function (extract URLs from search results)
def extract_urls(search_results):
    """
    Extract URLs from search result content using regular expressions.

    Args:
        search_results (str): Search result content as a single string.

    Returns:
        list: List of extracted URLs.
    """
    # Regular expression to match URLs inside parentheses or as plain text
    url_pattern = r"https?://[^\s\)]+"
    urls = re.findall(url_pattern, search_results)
    return urls


async def run_fetch_and_validate_task(user_id):
    """
    Run fetch and validate task in an asyncio loop.
    """
    try:
        await fetch_and_validate_replies(user_id)
    finally:
        set_is_fetch_and_validate_active(False)


def judge_bet(request: BetRequest):
    """
    Use Tavily search to directly determine the correctness of a bet.

    Args:
        request (BetRequest): Contains the bet description and optional URLs.

    Returns:
        bool: True if the bet is deemed valid, False otherwise.
    """
    try:
        # Use Tavily search to perform judgment based on description
        print("Performing Tavily search for:", request.description)
        keywords = ["rise", "fall", "increase", "decrease", "exceed", "below"]  # Example keywords for market bets
        is_valid = search_util.search_and_judge(query=request.description, keywords=keywords)
        print(is_valid)
        result = int(is_valid) + 1
        set_bet_result(request.address, result)
        return is_valid
    except Exception as e:
        print(f"Error in judge_bet: {e}")
        return False


@app.post("/validate_market")
async def validate_market(request: ValidateMarketRequest):
    """
    Validate the market description and return analysis results and steps.

    Args:
        request (ValidateMarketRequest): Contains the market description.

    Returns:
        dict: Includes analysis results and detailed processing steps.
    """
    try:
        # Call analyze_market function to process the description
        analyze_result, steps = validating_market(request.description, agent_executor, search_util)

        # Return the analysis result and steps
        return {
            "analyze_result": analyze_result,
            "steps": steps
        }
    except Exception as e:
        # Handle and return any exceptions
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")

# FastAPI endpoint
@app.post("/judge_bet")
async def judge_bet_endpoint(request: BetRequest):
    try:
        verdict = judge_bet(request)
        return {"verdict": verdict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/start_fetch_and_validate")
async def start_fetch_and_validate_replies(request: FetchAndAnalyzeRepliesRequest, background_tasks: BackgroundTasks):
    """
    Start fetching and validating replies as a background task.

    Args:
        user_id (str): The user ID to monitor.
        background_tasks (BackgroundTasks): FastAPI's background task manager.

    Returns:
        dict: Status message.
    """
    is_fetch_and_validate_active = get_is_fetch_and_validate_active()
    stop_fetch_and_validate_stop_event = get_fetch_and_validate_stop_event()

    user_id = request.user_id

    if is_fetch_and_validate_active:
        return {"status": 400, "message": "Fetch and validate process is already running."}

    set_is_fetch_and_validate_active(True)
    stop_fetch_and_validate_stop_event.clear()  # Ensure stop event is clear

    # Start the background task
    background_tasks.add_task(run_fetch_and_validate_task, user_id)
    return {"status": 200, "message": "Fetch and validate process started."}


@app.post("/stop_fetch_and_validate")
async def stop_fetch_and_validate():
    """
    Stop the fetch and validate background process.

    Returns:
        dict: Status message.
    """
    is_fetch_and_validate_active = get_is_fetch_and_validate_active()

    if not is_fetch_and_validate_active:
        return {"status": 400, "message": "Fetch and validate process is not running."}

    fetch_and_validate_stop_evnet = get_fetch_and_validate_stop_event()
    fetch_and_validate_stop_evnet.set()  # Signal to stop the task
    set_is_fetch_and_validate_active(False)
    return {"status": 200, "message": "Fetch and validate process stopped."}


@app.post("/post_tweet")
async def post_tweet_endpoint(request: PostTweetRequest):
    # get local time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = (
        f"🎉 Create Bet Successfully! 🎉\n"
        f"🏠 Contract Address: {request.address}\n"
        f"📜 Message: {request.message}\n"
        f"🔗 Explore: our product url\n"
        f"⏰ Timestamp: {current_time}\n\n"
        f"Powered by our platform 🚀"
    )

    result = await post_tweet(message)
    return {"status": 200, "message": "success", "data": result}


@app.post("/feed_back")
async def feed_back_endpoint(request: FeedbackRequest):
    message = request.message
    await collect_feedback_and_improve(message)
    return {"status": 200, "message": "success"}


@app.post("/self_introduction")
async def generate_self_intro_tweet_endpoint():
    result = await generate_self_intro_tweet()
    await post_tweet(result)
    return {"status": 200, "message": "success"}


