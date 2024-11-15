# main.py

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cdp_langchain.utils import CdpAgentkitWrapper
from cdp_langchain.agent_toolkits import CdpToolkit
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

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
    # Test case 1: Will it be sunny in Bangkok tomorrow?
    test_data1 = BetRequest(
        description="Will it be sunny in Bangkok tomorrow?",
        urls=["https://example.com/weather/bangkok-tomorrow"]
    )

    # Test case 2: Will the BTC price increase tomorrow?
    test_data2 = BetRequest(
        description="Will the BTC price increase tomorrow?",
        urls=["https://example.com/finance/btc-tomorrow"]
    )

    # Run tests
    verdict1 = judge_bet(test_data1)
    verdict2 = judge_bet(test_data2)

    # Output test results
    print("Test Case 1 - Will it be sunny in Bangkok tomorrow?")
    print("Judgment result:", "Victory" if verdict1 else "Failure")

    print("\nTest Case 2 - Will the BTC price increase tomorrow?")
    print("Judgment result:", "Victory" if verdict2 else "Failure")
