from cdp_langchain.utils import CdpAgentkitWrapper
from config.config import cdp_api_key_name, cdp_api_key_private_key
import json
import os


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
        # faucet = cdp.wallet.faucet()
        # faucet.wait()
        # print(faucet)

    return cdp
