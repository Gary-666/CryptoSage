import re
import json
from datetime import datetime
from dateutil.parser import parse
from llm.feedback import collect_feedback_and_improve


# Analyze the market description
def validating_market(description: str, agent_executor, search_util):
    """
    Analyze the market description and validate its components.

    Args:
        description (str): The market description.

    Returns:
        dict: Analysis results including completeness, outcomes, and verifiability.
    """
    steps = []

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
        # Record Step 1
        steps.append({
            "step": 1,
            "input": description,
            "description": "Check if the market description is valid.",
            "output": {
                "has_due_date": analysis_result["has_due_date"],
                "due_date": analysis_result["due_date"],
            }
        })
        # Proceed only if both due date and two outcomes are valid
        if has_due_date and has_two_outcomes:
            # Step 2: Use TavilySearchUtil to perform an online search
            search_results = search_util.search(description)
            content_list = search_util.extract_content(search_results)
            combined_content = " ".join(content_list)

            steps.append({
                "step": 2,
                "input": description,
                "description": "Check if the market has only two outcomes.",
                "output": {
                    "has_two_outcomes": analysis_result["has_two_outcomes"],
                }
            })

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

            # Record Step 3
            steps.append({
                "step": 3,
                "input": {"description": description, "combined_content": combined_content},
                "output": {
                    "is_verifable": analysis_result["is_valid"],
                }
            })
        else:
            analysis_result["is_valid"] = False
            steps.append({
                "step": "Step 2: Perform online search",
                "input": description,
                "output": "Skipped due to incomplete analysis result."
            })

    except Exception as e:
        print(f"Error during analysis: {e}")
        error_message = f"Error during analysis: {e}"
        steps.append({
            "step": "Step 1: Analyze market description",
            "input": description,
            "error": error_message
        })
    print(analysis_result)
    return analysis_result, steps

