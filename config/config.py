import os

from cdp_langchain.agent_toolkits import CdpToolkit
from cdp_langchain.utils import CdpAgentkitWrapper
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()

# load twitter cookies
COOKIES_JSON = os.getenv("TWITTER_COOKIES")
openai_api_key = os.getenv('OPENAI_API_KEY')
cdp_api_key_name = os.getenv('CDP_API_KEY_NAME')
cdp_api_key_private_key = os.getenv('CDP_API_KEY_PRIVATE_KEY')
tavily_api_key = os.getenv("TAVILY_API_KEY")

# Initialize CDP Wrapper and Toolkit
cdp = CdpAgentkitWrapper(api_key_name=cdp_api_key_name, api_key_private_key=cdp_api_key_private_key)
toolkit = CdpToolkit.from_cdp_agentkit_wrapper(cdp)

# Initialize LLM and create Agent
llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=openai_api_key)
tools = toolkit.get_tools()
agent_executor = create_react_agent(llm, tools)
