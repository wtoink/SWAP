import os
import json
import time
from dotenv import load_dotenv
from web3 import Web3

# Load ENV
load_dotenv()
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
RPC_URL = os.getenv("RPC_URL")
ROUTER_ADDRESS = os.getenv("ROUTER_ADDRESS")

# Connect RPC
web3 = Web3(Web3.HTTPProvider(RPC_URL))
if not web3.is_connected():
    raise Exception("⚠️ Gagal konek RPC!")

print(f"✅ Terkoneksi ke chain: {web3.eth.chain_id}")

# Load Router ABI
with open("abi.json", "r") as f:
    router_abi = json.load(f)

router = web3.eth.contract(address=Web3.to_checksum_address(ROUTER_ADDRESS), abi=router_abi)

# Setting token
WETH = web3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")  # WETH mainnet
TOKEN_OUT = web3.to_checksum_address("0xdAC17F958D2ee523a2206206994597C13D831ec7")  # USDT mainnet

def swap_eth_for_token(amount_in_eth, slippage=0.01):
    amount_in_wei = web3.to_wei(amount_in_eth, "ether")
    path = [WETH, TOKEN_OUT]
    deadline = int(time.time()) + 60 * 5  # 5 menit
    amount_out_min = 0  # bisa pakai quoter untuk real slippage

    tx = router.functions.swapExactETHForTokens(
        amount_out_min,
        path,
        WALLET_ADDRESS,
        deadline
    ).build_transaction({
        "from": WALLET_ADDRESS,
        "value": amount_in_wei,
        "gas": 250000,
        "gasPrice": web3.eth.gas_price,
        "nonce": web3.eth.get_transaction_count(WALLET_ADDRESS),
    })

    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"🚀 Swap dikirim! Tx Hash: {web3.to_hex(tx_hash)}")

# Jalankan swap contoh
if __name__ == "__main__":
    swap_eth_for_token(0.001)  # swap 0.001 ETH
