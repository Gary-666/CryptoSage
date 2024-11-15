# main.py

import os
import re
from datetime import datetime

from dateutil.parser import parse
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cdp_langchain.utils import CdpAgentkitWrapper
from cdp_langchain.agent_toolkits import CdpToolkit
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from utils.tavily_search import TavilySearchUtil, tavily_api_key
import json


# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
cdp_api_key_name = os.getenv('CDP_API_KEY_NAME')
cdp_api_key_private_key = os.getenv('CDP_API_KEY_PRIVATE_KEY')

# Initialize CDP Wrapper and Toolkit
cdp = CdpAgentkitWrapper(api_key_name=cdp_api_key_name, api_key_private_key=cdp_api_key_private_key)
toolkit = CdpToolkit.from_cdp_agentkit_wrapper(cdp)

# Initialize LLM and create Agent
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)
tools = toolkit.get_tools()
agent_executor = create_react_agent(llm, tools)

# Initialize Tavily Search Utility
search_util = TavilySearchUtil(api_key=tavily_api_key)



# FastAPI application
app = FastAPI()


# Request data model
class BetRequest(BaseModel):
    description: str  # Bet description (e.g., weather in Bangkok tomorrow)
    urls: list = []  # Optional list of data source URLs for LLM to query


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


# Analyze the market description
def analyze_market(description: str) -> dict:
    """
    Analyze the market description and validate its components.

    Args:
        description (str): The market description.

    Returns:
        dict: Analysis results including completeness, outcomes, and verifiability.
    """
    analysis_result = {
        "has_due_date": False,
        "due_date": None,
        "has_two_outcomes": False,
        "outcomes": [],
        "is_valid": False  # Indicates if the bet is realistic and valid
    }

    # Step 1: Use LLM to extract due date and outcomes
    analyze_query = f"""
    Please analyze the following market description and return the results in JSON format.
    The JSON should include:
    - "has_due_date": Whether the description contains a due date (true/false).
    - "due_date": The due date in ISO format (if available), or null.
    - "has_two_outcomes": Whether the description is a binary question (true/false).
    - "outcomes": A list of possible outcomes (up to two, e.g., ["Yes", "No"]).
    
    Description: "{description}"
    """

    try:
        # Use the `stream` method to process LLM response
        analyze_event = agent_executor.stream(
            {"messages": [("user", analyze_query)]}, stream_mode="values"
        )
        analyze_response = [event["messages"][-1].content for event in analyze_event]
        response_text = analyze_response[-1]

        cleaned_content = re.sub(r"```(?:json)?", "", response_text).strip()
        parsed_response = json.loads(cleaned_content)

        # Extract fields from parsed response
        has_due_date = parsed_response.get("has_due_date", False)
        has_two_outcomes = parsed_response.get("has_two_outcomes", False)
        due_date_str = parsed_response.get("due_date")
        outcomes = parsed_response.get("outcomes", [])

        analysis_result["has_due_date"] = has_due_date
        analysis_result["has_two_outcomes"] = has_two_outcomes
        analysis_result["outcomes"] = outcomes

        if has_due_date and due_date_str:
            # Try to standardize the due date
            try:
                due_date = parse(due_date_str, fuzzy=True)
                analysis_result["due_date"] = due_date.isoformat()
            except Exception:
                analysis_result["has_due_date"] = False
                analysis_result["due_date"] = None
        else:
            analysis_result["due_date"] = None

        # Proceed only if both due date and two outcomes are valid
        if has_due_date and has_two_outcomes:
            # Step 2: Use TavilySearchUtil to perform an online search
            search_results = search_util.search(description)
            content_list = search_util.extract_content(search_results)
            combined_content = " ".join(content_list)

            # Step 3: Pass the search results to LLM to judge if the bet is valid
            validation_query = f"""
                Given the following market description and relevant information, determine if the bet is realistic and valid.

                Market Description: "{description}"

                Relevant Information: "{combined_content}"

                Please answer with "true" if the bet is realistic and valid, or "false" if the bet is unrealistic or invalid.
                """

            validation_event = agent_executor.stream(
                {"messages": [("user", validation_query)]},
                stream_mode="values"
            )
            validation_response = [
                event["messages"][-1].content for event in validation_event
            ]
            validation_text = validation_response[-1].strip().lower()

            if "true" in validation_text:
                analysis_result["is_valid"] = True
            else:
                analysis_result["is_valid"] = False
        else:
            analysis_result["is_valid"] = False

    except Exception as e:
        print(f"Error during analysis: {e}")
    print(analysis_result)
    return analysis_result


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
@app.post("/judge_bet/")
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
    result = analyze_market(test_description)
    print("Market Analysis Result:", result)
