from cdp_langchain.utils import CdpAgentkitWrapper
from dotenv import load_dotenv

import json
import os

# Load environment variables
load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
cdp_api_key_name = os.getenv('CDP_API_KEY_NAME')
cdp_api_key_private_key = os.getenv('CDP_API_KEY_PRIVATE_KEY')
tavily_api_key = os.getenv("TAVILY_API_KEY")


def init_cdp_agent_kit() -> CdpAgentkitWrapper:
    conf = {
        "api_key_name": cdp_api_key_name,
        "api_key_private_key": cdp_api_key_private_key,
        "network_id": "polygon-mainnet",
    }
    if os.path.exists("wallet.json"):
        wallet = json.load(open("wallet.json", "r"))
        conf["cdp_wallet_data"] = wallet

    cdp = CdpAgentkitWrapper(**conf)

    if not os.path.exists("wallet.json"):
        wallet = cdp.export_wallet()
        json.dump(wallet, open("wallet.json", "w"))
        # faucet = CDP.wallet.faucet()
        # faucet.wait()
        # print(faucet)

    return cdp
