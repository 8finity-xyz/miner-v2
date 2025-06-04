import sys

v = sys.version_info
if v < (3, 10):
    print(
        f"[ERROR] Unsuported python version, please upgrade to version 3.10 or higher. Your version: python{v[0]}.{v[1]}"
    )
    exit(0)

import logging
import os

import dotenv
from eth_account import Account
from eth_utils import is_same_address
from web3 import Web3

dotenv.load_dotenv()


logging.basicConfig(
    level=os.getenv("LOGLEVEL", "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

POOL_URL = os.getenv("INFINITY_POOL_URL")
POOL_MODE = POOL_URL is not None and POOL_URL != ""


# Node Config
RPC = os.getenv("INFINITY_RPC", "https://rpc.soniclabs.com")
WS = os.getenv("INFINITY_WS", "wss://rpc.soniclabs.com")

# Common miner config
MINER_PRIVATE_KEY = os.getenv("INFINITY_MINER_PRIVATE_KEY")
REWARDS_RECIPIENT_ADDRESS = os.getenv("INFINITY_REWARDS_RECIPIENT_ADDRESS")


# ============ Config validation ============
def validate_solo_params():
    global RPC, WS, MINER_PRIVATE_KEY, REWARDS_RECIPIENT_ADDRESS

    if MINER_PRIVATE_KEY is None:
        print(
            "[ERROR]: INFINITY_MINER_PRIVATE_KEY is missing. Please set it in your .env file."
        )
        exit(0)

    try:
        miner_account = Account.from_key(MINER_PRIVATE_KEY)
    except Exception:
        pk = (
            MINER_PRIVATE_KEY[:4]
            + "*" * (len(MINER_PRIVATE_KEY) - 8)
            + MINER_PRIVATE_KEY[-4:]
        )
        print(
            f"[ERROR]: The value provided for INFINITY_MINER_PRIVATE_KEY ({pk}) is not a valid private key."
        )
        exit(0)

    if REWARDS_RECIPIENT_ADDRESS is None:
        REWARDS_RECIPIENT_ADDRESS = miner_account.address

    if not is_same_address(miner_account.address, REWARDS_RECIPIENT_ADDRESS):
        print(
            f"[WARNING]: Make sure you have access to the INFINITY_REWARDS_RECIPIENT_ADDRESS ({REWARDS_RECIPIENT_ADDRESS})."
        )

    try:
        w3 = Web3(Web3.HTTPProvider(RPC))
        miner_balance = w3.eth.get_balance(miner_account.address)
    except Exception:
        print(f"[ERROR]: Unable to establish a connection with INFINITY_RPC ({RPC}).")
        exit(0)

    if miner_balance < 10e18:
        print(
            f"[WARNING]: Current master balance is {miner_balance/1e18:.2f} $S. Consider topping it up."
        )


def validate_pool_params():
    global POOL_URL, REWARDS_RECIPIENT_ADDRESS

    import urllib.request

    try:
        with urllib.request.urlopen(POOL_URL + "/healthcheck") as response:
            assert response.status == 200
    except Exception as e:
        print(e)
        print(
            f"[ERROR]: Unable to establish a connection with INFINITY_POOL_URL ({POOL_URL})."
        )
        exit(0)


if POOL_MODE:
    validate_pool_params()
else:
    validate_solo_params()
