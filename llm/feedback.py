# openai_api/emoticon_gen.py
import json
import re

from openai import OpenAI

from config.config import openai_api_key

ai_client = OpenAI(api_key=openai_api_key)


# In-memory storage for user feedback
feedback_storage = []


async def collect_feedback_and_improve(new_feedback: dict):
    """
    Collect user feedback and generate improved validation prompts.

    Args:
        new_feedback (dict): A dictionary containing user feedback.
            Example:
            {
                "clarity": "The outcomes seem ambiguous.",
                "suggestion": "Please include more guidance on the due date format."
            }

    Returns:
        dict: A dictionary containing the original feedback and the improved validation prompt.
        Example output:
        {
            "feedback_summary": "The outcomes are too vague, and the due date is unclear.",
            "improved_prompt": "Ensure the market description specifies clear outcomes and includes a precise due date in ISO format."
        }
    """
    try:
        # Add the new feedback to the in-memory storage
        feedback_storage.append(new_feedback)

        # Construct a dynamic prompt by aggregating all feedback
        feedback_messages = "\n".join([
            f"Feedback {i + 1}:\n"
            f"1. Clarity: {fb['clarity']}\n"
            f"2. Suggestion: {fb['suggestion']}\n"
            for i, fb in enumerate(feedback_storage)
        ])

        # Send the aggregated feedback to the AI model to generate a new prompt
        response = ai_client.chat.completions.create(
            model="o1-model",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are an AI assistant refining validation prompts based on user feedback.
                    Users provide feedback on two aspects:
                    1. How clear and specific the description is.
                    2. Suggestions for improvement.

                    Based on the provided feedback, generate a concise JSON object with:
                    - "feedback_summary": A summary of common issues (10-30 words).
                    - "improved_prompt": A revised validation prompt based on the feedback.

                    Example output:
                    {
                        "feedback_summary": "The outcomes are too vague, and the due date is unclear.",
                        "improved_prompt": "Ensure the market description specifies clear outcomes and includes a precise due date in ISO format."
                    }
                    """
                },
                {
                    "role": "user",
                    "content": f"Here is the accumulated feedback:\n{feedback_messages}\nPlease generate an improved validation prompt."
                }
            ]
        )

        # Extract the improved prompt from the response
        content = response.choices[0].message.content
        cleaned_content = re.sub(r"```(?:json)?", "", content).strip()
        feedback_data = json.loads(cleaned_content)

        return feedback_data

    except Exception as e:
        print("Error generating feedback:", e)
        return None