
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

abi = [
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [],
		"name": "ReentrancyGuardReentrantCall",
		"type": "error"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "initiator",
				"type": "address"
			}
		],
		"name": "BetCancelled",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "participant",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "value",
				"type": "uint256"
			}
		],
		"name": "BetClaimed",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "initiator",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "address",
				"name": "token",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "minValue",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "string",
				"name": "message",
				"type": "string"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "endTime",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "address",
				"name": "judge",
				"type": "address"
			}
		],
		"name": "BetOpened",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "participant",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "value",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint8",
				"name": "bet",
				"type": "uint8"
			}
		],
		"name": "BetPlaced",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint8",
				"name": "result",
				"type": "uint8"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "judge",
				"type": "address"
			}
		],
		"name": "BetResultSet",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "bool",
				"name": "_result",
				"type": "bool"
			},
			{
				"internalType": "uint256",
				"name": "_value",
				"type": "uint256"
			}
		],
		"name": "bet",
		"outputs": [],
		"stateMutability": "payable",
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
		"name": "betValues",
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
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "bets",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "value",
				"type": "uint256"
			},
			{
				"internalType": "uint8",
				"name": "bet",
				"type": "uint8"
			},
			{
				"internalType": "bool",
				"name": "isClaimed",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "cancel",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "claim",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "endTime",
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
		"inputs": [],
		"name": "initiator",
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
		"name": "judge",
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
		"name": "message",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "minValue",
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
				"internalType": "address",
				"name": "_initiator",
				"type": "address"
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
				"internalType": "string",
				"name": "_message",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "_endTime",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "_judge",
				"type": "address"
			}
		],
		"name": "open",
		"outputs": [],
		"stateMutability": "nonpayable",
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
		"name": "participants",
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
		"inputs": [
			{
				"internalType": "uint8",
				"name": "_result",
				"type": "uint8"
			}
		],
		"name": "setResult",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "state",
		"outputs": [
			{
				"internalType": "enum LazyBet.BetState",
				"name": "",
				"type": "uint8"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "token",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

cdp = init_cdp_agent_kit()
agent_wallet = cdp.wallet
# contract_addr = '0xB93138dA9c65e85d6d97c795029F1D269d512b65'
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
    print(invocation)
    # res = invocation.wait()


def set_bet_result(address: str, result: bool):
    args = {
        '_result': result
    }

    invocation = agent_wallet.invoke_contract(
        contract_address=address, abi=abi, method='setResult', args=args)
    # res = invocation.wait()
    # print(res)

