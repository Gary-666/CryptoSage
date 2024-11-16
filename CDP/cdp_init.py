from cdp_langchain.utils import CdpAgentkitWrapper
import json
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

cdp_api_key_name = os.getenv('CDP_API_KEY_NAME')
cdp_api_key_private_key = os.getenv('CDP_API_KEY_PRIVATE_KEY')


def init_cdp_agent_kit() -> CdpAgentkitWrapper:
    conf = {
        "api_key_name": cdp_api_key_name,
        "api_key_private_key": cdp_api_key_private_key,
        "network_id": "base-sepolia",
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
