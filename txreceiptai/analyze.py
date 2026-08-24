from __future__ import annotations
from dataclasses import asdict, dataclass
import re

class DecodeError(ValueError):
    pass

_ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]{40}\Z")
_HASH_RE = re.compile(r"0x[0-9a-fA-F]{64}\Z")

def _evm_address(value: object, name: str) -> str:
    if not isinstance(value, str) or _ADDRESS_RE.fullmatch(value) is None:
        raise DecodeError(f"{name} must be a 20-byte 0x-prefixed address")
    return value.lower()

def _hex_int(value: object, name: str, *, optional: bool = False) -> int | None:
    if value is None and optional:
        return None
    if not isinstance(value, str) or not value.startswith("0x"):
        raise DecodeError(f"{name} must be a 0x-prefixed hex quantity")
    try:
        return int(value, 16)
    except ValueError as exc:
        raise DecodeError(f"{name} is not hexadecimal") from exc

def _address(word: str) -> str:
    if len(word) != 64 or any(char not in "0123456789abcdefABCDEF" for char in word):
        raise DecodeError("calldata contains an invalid ABI word")
    if int(word[:24], 16) != 0:
        raise DecodeError("address ABI word has nonzero padding")
    return "0x" + word[-40:].lower()

def _uint(word: str) -> int:
    if len(word) != 64:
        raise DecodeError("calldata contains a truncated ABI word")
    try:
        return int(word, 16)
    except ValueError as exc:
        raise DecodeError("calldata ABI word is not hexadecimal") from exc

def decode_calldata(value: object) -> dict[str, object]:
    if value in (None, "0x", ""):
        return {"selector": None, "method": "native-transfer-or-empty", "arguments": {}}
    if not isinstance(value, str) or not value.startswith("0x"):
        raise DecodeError("transaction input must be 0x-prefixed hex")
    raw = value[2:]
    if len(raw) < 8 or len(raw) % 2 or any(char not in "0123456789abcdefABCDEF" for char in raw):
        raise DecodeError("transaction input is malformed")
    selector, body = raw[:8].lower(), raw[8:]
    specs = {
        "a9059cbb": ("transfer(address,uint256)", ("to", "address"), ("amount", "uint")),
        "095ea7b3": ("approve(address,uint256)", ("spender", "address"), ("amount", "uint")),
        "23b872dd": ("transferFrom(address,address,uint256)", ("from", "address"), ("to", "address"), ("amount", "uint")),
        "a22cb465": ("setApprovalForAll(address,bool)", ("operator", "address"), ("approved", "bool")),
    }
    spec = specs.get(selector)
    if spec is None:
        return {"selector": "0x" + selector, "method": "unknown", "arguments": {}, "calldata_bytes": len(raw) // 2}
    method, *arguments = spec
    if len(body) != 64 * len(arguments):
        raise DecodeError(f"{method} calldata has unexpected length")
    decoded: dict[str, object] = {}
    for index, (name, kind) in enumerate(arguments):
        word = body[index * 64:(index + 1) * 64]
        number = _uint(word)
        if kind == "address":
            decoded[name] = _address(word)
        elif kind == "bool":
            if number not in (0, 1):
                raise DecodeError("boolean ABI word must be 0 or 1")
            decoded[name] = bool(number)
        else:
            decoded[name] = number
    return {"selector": "0x" + selector, "method": method, "arguments": decoded}

@dataclass(frozen=True, slots=True)
class Evidence:
    transaction_hash: str
    block_number: int
    status: str
    from_address: str
    to_address: str | None
    native_value_wei: int
    gas_used: int
    effective_gas_price_wei: int | None
    transaction_fee_wei: int | None
    calldata: dict[str, object]
    log_count: int

def analyze_bundle(transaction: dict[str, object], receipt: dict[str, object]) -> dict[str, object]:
    if not isinstance(transaction, dict) or not isinstance(receipt, dict):
        raise DecodeError("bundle transaction and receipt must be objects")
    tx_hash = transaction.get("hash")
    if not isinstance(tx_hash, str) or _HASH_RE.fullmatch(tx_hash) is None:
        raise DecodeError("transaction hash must be a 32-byte 0x-prefixed value")
    if receipt.get("transactionHash") != tx_hash:
        raise DecodeError("transaction and receipt hashes do not match")
    block_tx = _hex_int(transaction.get("blockNumber"), "transaction.blockNumber")
    block_receipt = _hex_int(receipt.get("blockNumber"), "receipt.blockNumber")
    if block_tx != block_receipt:
        raise DecodeError("transaction and receipt block numbers do not match")
    status_value = _hex_int(receipt.get("status"), "receipt.status")
    if status_value not in (0, 1):
        raise DecodeError("receipt status must be 0x0 or 0x1")
    gas = _hex_int(receipt.get("gasUsed"), "receipt.gasUsed")
    price = _hex_int(receipt.get("effectiveGasPrice"), "receipt.effectiveGasPrice", optional=True)
    sender = _evm_address(transaction.get("from"), "transaction.from")
    recipient_value = transaction.get("to")
    recipient = None if recipient_value is None else _evm_address(recipient_value, "transaction.to")
    logs = receipt.get("logs", [])
    if not isinstance(logs, list):
        raise DecodeError("receipt.logs must be an array")
    evidence = Evidence(tx_hash.lower(), block_tx or 0, "success" if status_value == 1 else "reverted", sender, recipient, _hex_int(transaction.get("value"), "transaction.value") or 0, gas or 0, price, (gas or 0) * price if price is not None else None, decode_calldata(transaction.get("input")), len(logs))
    return {"evidence": asdict(evidence), "limitations": ["method decoding covers four fixed ABI signatures only", "token symbols, prices, intent, safety, and contract identity are not inferred", "receipt facts do not prove that an interaction was beneficial or authorized"]}
