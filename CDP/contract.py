
from CDP.cdp_init import init_cdp_agent_kit

factory_abi = [
    {
        "inputs": [],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            }
        ],
        "name": "OwnableInvalidOwner",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            }
        ],
        "name": "OwnableUnauthorizedAccount",
        "type": "error"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "betAddress",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "initiator",
                "type": "address"
            }
        ],
        "name": "BetCreated",
        "type": "event"
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "previousOwner",
                "type": "address"
            },
            {
                "indexed": True,
                "internalType": "address",
                "name": "newOwner",
                "type": "address"
            }
        ],
        "name": "OwnershipTransferred",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "allBets",
        "outputs": [
            {
                "internalType": "address[]",
                "name": "",
                "type": "address[]"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "name": "bets",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "betsCount",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_message",
                "type": "string"
            },
            {
                "internalType": "address",
                "name": "_token",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "_minValue",
                "type": "uint256"
            },
            {
                "internalType": "address",
                "name": "_judge",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "_endTime",
                "type": "uint256"
            }
        ],
        "name": "createBet",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "lazyBetBytecode",
        "outputs": [
            {
                "internalType": "bytes",
                "name": "",
                "type": "bytes"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "renounceOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes",
                "name": "_lazyBetBytecode",
                "type": "bytes"
            }
        ],
        "name": "setLazyBetBytecode",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "newOwner",
                "type": "address"
            }
        ],
        "name": "transferOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

cdp = init_cdp_agent_kit()
agent_wallet = cdp.wallet
# contract_addr = '0xB93138dA9c65e85d6d97c795029F1D269d512b65'
# contract_addr = '0x5882b508bbDe4a1B1A20E425Fbb3FfF19c3fc8A4'
contract_addr = '0x11165e9afa37d76c6d032961c63d14ee8efd68c7'

# def call_contract(contract_address: str, method: str, args: dict):
#     invocation = agent_wallet.invoke_contract(
#         contract_address=contract_address, contract_abi=abi, method=method, args=args)
#     invocation.wait()


def create_bet(message, token, min_value, judge, end_time):
    args = {
        '_message': message,
        '_token': token,
        '_minValue': str(min_value),
        '_judge': judge,
        '_endTime': str(end_time)
    }

    invocation = agent_wallet.invoke_contract(
        contract_address=contract_addr, abi=factory_abi, method='createBet', args=args)
    res = invocation.wait()
    print(res)

    # 提取新合约地址（假设返回值包含部署的合约地址）
    new_contract_address = res.get("result")  # 根据具体的返回结构获取合约地址
    print(f"Newly Deployed Contract Address: {new_contract_address}")

    return new_contract_address

# create_bet("test",
#            "0x0000000000000000000000000000000000000000",
#            1,
#            "0x0000000000000000000000000000000000000000",
#            1731734021)
