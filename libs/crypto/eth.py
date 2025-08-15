import os, requests
from libs.common.config import ETHERSCAN_API_KEY, ETH_RPC_URL

def etherscan_txs(address: str, startblock=0, endblock=99999999, sort="desc"):
    if not ETHERSCAN_API_KEY:
        raise RuntimeError("ETHERSCAN_API_KEY missing")
    url = ("https://api.etherscan.io/api"
           f"?module=account&action=txlist&address={address}&startblock={startblock}&endblock={endblock}&sort={sort}&apikey={ETHERSCAN_API_KEY}")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "1":
        return []
    return data["result"]

def rpc_get_balance(address: str):
    if not ETH_RPC_URL:
        raise RuntimeError("ETH_RPC_URL missing")
    payload = {"jsonrpc":"2.0","method":"eth_getBalance","params":[address,"latest"],"id":1}
    r = requests.post(ETH_RPC_URL, json=payload, timeout=30)
    r.raise_for_status()
    return int(r.json()["result"],16)
