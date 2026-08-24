from __future__ import annotations
import json
from urllib import request

def rpc_call(endpoint: str, method: str, params: list[object], *, timeout: float = 30.0) -> object:
    if method not in {"eth_getTransactionByHash", "eth_getTransactionReceipt"}:
        raise ValueError("TxReceiptAI permits read-only transaction RPC methods only")
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req = request.Request(endpoint, data=body, headers={"Content-Type":"application/json"})
    with request.urlopen(req, timeout=timeout) as response:
        payload = json.load(response)
    if payload.get("error"):
        raise ValueError(f"RPC error: {payload['error']}")
    return payload.get("result")
