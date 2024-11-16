# openai_api/emoticon_gen.py
import json
import re

from openai import OpenAI

from config.config import openai_api_key

ai_client = OpenAI(api_key=openai_api_key)


# Collect feedback and generate improved validation prompts
async def collect_feedback_and_improve():
    """
    Collect feedback on AI-generated market descriptions and use it to generate
    improved validation prompts for the LLM.

    Returns:
        dict: A dictionary containing the original feedback and the improved validation prompt.
    """
    try:
        # Send a generation request to get feedback prompts
        response = ai_client.chat.completions.create(
            model="o1-model",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are an AI assistant helping refine market descriptions for bets. 
                    Users provide feedback on two aspects:
                    1. How clear and specific the description is.
                    2. Suggestions for improvement.

                    Please format your output as a JSON object with two fields:
                    - "feedback_summary": A concise summary (10-30 words) of the feedback.
                    - "improved_prompt": A revised validation prompt based on the feedback.

                    Example:
                    {
                        "feedback_summary": "The outcomes are too vague, and the due date is unclear.",
                        "improved_prompt": "Ensure the market description specifies clear outcomes and includes a precise due date in ISO format."
                    }

                    Only output the JSON object. No additional text.
                    """
                },
                {
                    "role": "user",
                    "content": """
                    User Feedback:
                    1. "The outcomes seem ambiguous. It's not clear what counts as 'success'."
                    2. "Please include more guidance on what format the due date should follow."
                    """
                }
            ]
        )

        # Extract the response
        content = response.choices[0].message.content

        # Parse the content as JSON
        cleaned_content = re.sub(r"```(?:json)?", "", content).strip()
        feedback_data = json.loads(cleaned_content)
        return feedback_data

    except Exception as e:
        print("Error generating feedback:", e)
        return None
