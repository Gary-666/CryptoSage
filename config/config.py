import os
import ssl

import redis.asyncio as redis
from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()

# load twitter cookies
twitter_cookies = os.getenv("TWITTER_COOKIES")
cookies_path = os.getenv("COOKIES_PATH", "")
twitter_email = os.getenv("TWITTER_EMAIL", "")
twitter_password = os.getenv("TWITTER_PASSWORD", "")
twitter_username = os.getenv("TWITTER_USERNAME", "")

# load redis from localhost
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_TLS = os.getenv("REDIS_TLS", "false").lower() == "true"
REDIS_SNI = os.getenv("REDIS_SNI", None)

discord_token = os.getenv("DISCORD_TOKEN", "")

openai_api_key = os.getenv('OPENAI_API_KEY')
cdp_api_key_name = os.getenv('CDP_API_KEY_NAME')
cdp_api_key_private_key = os.getenv('CDP_API_KEY_PRIVATE_KEY')
tavily_api_key = os.getenv("TAVILY_API_KEY")


# Initialize CDP Wrapper and Toolkit
# cdp = CdpAgentkitWrapper(api_key_name=cdp_api_key_name, api_key_private_key=cdp_api_key_private_key)
# toolkit = CdpToolkit.from_cdp_agentkit_wrapper(cdp)

# Initialize LLM and create Agent
# llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)
# tools = toolkit.get_tools()
# agent_executor = create_react_agent(llm, tools)


# set SSL 和 SNI
ssl_context = None
if REDIS_TLS:
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    if REDIS_SNI:
        ssl_context.check_hostname = True

protocol = "rediss" if REDIS_TLS else "redis"
redis_url = f"{protocol}://{REDIS_HOST}:{REDIS_PORT}"

redis_client = redis.from_url(
    redis_url,
    password=REDIS_PASSWORD,
    db=REDIS_DB,
)
