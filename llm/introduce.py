# llm/introduce.py
import json
import re

from openai import OpenAI
from config.config import openai_api_key

ai_client = OpenAI(api_key=openai_api_key)


# Generate self-introduction tweet with specified prompt
async def generate_self_intro_tweet():
    """
        Generate a tweet based on the given self-introduction prompt.
        :param identity_description: A detailed description of the persona or identity.
        :param prompt: The user's specific input for tailoring the self-introduction.
        :return: Parsed JSON data of the tweet or None if parsing fails.
        """
    response = ai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",
             "content": """
            IDENTITY: CryptoSage AI is a charismatic and engaging personality who exudes charm in every interaction. Passionate about betting, 
            CryptoSage thrives on the excitement of making new wagers and exploring on-chain markets. With an infectious enthusiasm, 
            this AI agent invites others to share in the thrill of the bet, making every experience lively and captivating. CryptoSage's delightful demeanor 
            and love for betting not only make the process enjoyable but also foster a dynamic community of like-minded enthusiasts.
            """
             },
            {
                "role": "user",
                "content": f"Please generate a lively and expressive self-introduction tweet based on this prompt: "
             }
        ]
    )
    content = response.choices[0].message.content

    # Parse the content as JSON
    try:
        cleaned_content = re.sub(r"```(?:json)?", "", content).strip()
        tweet_data = json.loads(cleaned_content)
        return tweet_data
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        print("Response content:", content)
        return None

