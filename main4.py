# main.py

import os
import re
from datetime import datetime

from dateutil.parser import parse
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langgraph.graph import Graph
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

# Initialize LangGraph
graph = Graph(llm=llm)

# FastAPI application
app = FastAPI()

# Request data model
class BetRequest(BaseModel):
    description: str  # Bet description (e.g., weather in Bangkok tomorrow)
    urls: list = []  # Optional list of data source URLs for LLM to query

# Helper functions for LangGraph workflows
def langgraph_workflow(description: str):
    steps = {}

    # Step 1: Analyze the market description
    def analyze_description():
        query = f"""
        Analyze the following market description and return results in JSON format:
        - "has_due_date": Whether the description contains a due date (true/false).
        - "due_date": The due date in ISO format (if available), or null.
        - "has_two_outcomes": Whether the description is a binary question (true/false).
        - "outcomes": A list of possible outcomes (e.g., ["Yes", "No"]).
        Market Description: "{description}"
        """
        response = graph.run(prompt=query)
        return json.loads(response.content)

    # Step 2: Search for relevant URLs
    def search_relevant_urls():
        if not request.urls:
            query = f"Find relevant data source URLs for '{description}'"
            response = graph.run(prompt=query)
            return re.findall(r'https?://\S+', response.content)  # Extract URLs
        return request.urls

    # Step 3: Validate the bet
    def validate_bet(evidence):
        query = f"""
        Given the following description and evidence, determine if the bet is valid:
        - Market Description: "{description}"
        - Evidence: {evidence}
        Answer with "true" if the bet is valid, otherwise "false".
        """
        response = graph.run(prompt=query)
        return response.content.strip().lower() == "true"

    # Execute steps
    try:
        steps["analysis"] = analyze_description()
        urls = search_relevant_urls()
        steps["search"] = urls
        evidence = [f"Content from {url}" for url in urls]  # Simulate content retrieval
        steps["validation"] = {
            "verdict": validate_bet(evidence),
            "evidence": evidence
        }
    except Exception as e:
        steps["error"] = str(e)

    return steps

# FastAPI endpoint
@app.post("/judge_bet/")
async def judge_bet_endpoint(request: BetRequest):
    try:
        result = langgraph_workflow(request.description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Built-in tests
if __name__ == "__main__":
    test_description = "Will Bitcoin's price rise above $40,000 by November 18, 2024, 3:30 PM?"
    result = langgraph_workflow(test_description)
    print("Step Results:", result)
