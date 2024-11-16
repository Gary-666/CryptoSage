# utils/tavily_search.py

import os

from dotenv import load_dotenv
from tavily import TavilyClient
from typing import List, Dict

from config.config import tavily_api_key

# Load environment variables
load_dotenv()


class TavilySearchUtil:
    """
    A utility for performing searches using the Tavily API and processing the results.
    """

    def __init__(self, api_key: str):
        """
        Initialize the TavilySearchUtil with the provided API key.

        Args:
            api_key (str): The Tavily API key for authenticating requests.
        """
        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str, search_depth: str = "basic") -> List[Dict]:
        """
        Perform a search query using the Tavily API.

        Args:
            query (str): The search query string.
            search_depth (str): Depth of the search. Options: "basic", "advanced".

        Returns:
            List[Dict]: A list of search results with titles, URLs, and content.
        """
        try:
            response = self.client.search(query, search_depth=search_depth)
            return response.get("results", [])
        except Exception as e:
            raise RuntimeError(f"Failed to perform search: {str(e)}")

    def extract_urls(self, results: List[Dict]) -> List[str]:
        """
        Extract URLs from the Tavily search results.

        Args:
            results (List[Dict]): Search results returned by the Tavily API.

        Returns:
            List[str]: A list of URLs extracted from the search results.
        """
        return [result.get("url", "") for result in results if "url" in result]

    def extract_content(self, results: List[Dict]) -> List[str]:
        """
        Extract textual content from the Tavily search results.

        Args:
            results (List[Dict]): Search results returned by the Tavily API.

        Returns:
            List[str]: A list of content strings extracted from the search results.
        """
        return [result.get("content", "") for result in results if "content" in result]

    def search_and_judge(self, query: str, keywords: List[str], search_depth: str = "basic") -> bool:
        """
        Perform a search query and judge whether the content matches the specified keywords.

        Args:
            query (str): The search query string.
            keywords (List[str]): A list of keywords to look for in the search content.
            search_depth (str): Depth of the search. Options: "basic", "advanced".

        Returns:
            bool: True if any of the keywords are found in the search content; otherwise, False.
        """
        results = self.search(query, search_depth=search_depth)
        print(results)
        content_list = self.extract_content(results)
        print(content_list)
        combined_content = " ".join(content_list)
        return any(keyword in combined_content for keyword in keywords)


# Initialize Tavily Search Utility
search_util = TavilySearchUtil(api_key=tavily_api_key)

# Example usage:
if __name__ == "__main__":
    # Replace with your Tavily API key
    TAVILY_API_KEY = tavily_api_key

    # Initialize the utility
    search_util = TavilySearchUtil(api_key=TAVILY_API_KEY)

    # Define a query and keywords
    query = "What is the weather in Bangkok tomorrow?"
    keywords = ["sunny", "clear skies", "rain"]

    # Perform the search and judgment
    is_sunny = search_util.search_and_judge(query=query, keywords=keywords)

    # Output the judgment result
    print("Judgment result:", "Yes, it matches the keywords." if is_sunny else "No, it doesn't match the keywords.")
