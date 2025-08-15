import requests
from libs.common.config import BLOCKSTREAM_API_BASE

def address_txs(addr: str):
    r = requests.get(f"{BLOCKSTREAM_API_BASE}/address/{addr}/txs")
    r.raise_for_status()
    return r.json()

def tx_details(txid: str):
    r = requests.get(f"{BLOCKSTREAM_API_BASE}/tx/{txid}")
    r.raise_for_status()
    return r.json()
