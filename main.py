# main.py

from datetime import datetime

from dateutil.parser import parse

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config.config import agent_executor
from llm.validate import validating_market
from utils.tavily_search import search_util

# FastAPI application
app = FastAPI()


# Request data model
class BetRequest(BaseModel):
    description: str  # Bet description (e.g., weather in Bangkok tomorrow)
    urls: list = []  # Optional list of data source URLs for LLM to query


#  Request model for validate_market API
class ValidateMarketRequest(BaseModel):
    description: str  # Market description as input


# LLM judgment function
def judge_bet(request: BetRequest):
    # If the user did not provide URLs, let the LLM automatically search for relevant data sources
    if not request.urls:
        search_query = f"Please provide relevant data source URLs for '{request.description}'"
        search_event = agent_executor.stream({"messages": [("user", search_query)]}, stream_mode="values")
        search_results = [event["messages"][-1].content for event in search_event]
        request.urls = extract_urls(search_results[0])

    # Retrieve content from each URL
    evidence = []
    for url in request.urls:
        fetch_query = f"Please retrieve information from the following URL: {url}"
        fetch_event = agent_executor.stream({"messages": [("user", fetch_query)]}, stream_mode="values")
        content = [event["messages"][-1].content for event in fetch_event]
        evidence.append(content[0])

    # Determine the result (True / False) based on evidence and description
    verdict = determine_verdict(evidence, request.description)
    return verdict


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


# Verdict determination function
def determine_verdict(evidence, description):
    # Simplified logic (determines verdict based on whether evidence contains specific keywords)
    if any(keyword in " ".join(evidence) for keyword in ["晴", "上涨"]):  # "晴" = sunny, "上涨" = increase
        return True
    return False


# URL extraction function (extract URLs from search results)
def extract_urls(search_results):
    urls = []
    for result in search_results.split():
        if result.startswith("http"):
            urls.append(result)
    return urls


# FastAPI endpoint
@app.post("/judge_bet")
async def judge_bet_endpoint(request: BetRequest):
    try:
        verdict = judge_bet(request)
        return {"verdict": verdict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Built-in tests
if __name__ == "__main__":
    # Example market description
    test_description = "Will Bitcoin's price rise above $40,000 by November 18, 2024, 3:30 PM?"
    result, steps = validating_market(test_description, agent_executor, search_util)
    print("Market Analysis Result:", result)
    print("Market Analysis steps", steps)
