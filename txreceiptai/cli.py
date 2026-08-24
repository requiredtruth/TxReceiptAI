from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
from .analyze import DecodeError, analyze_bundle
from .rpc import rpc_call
from .explain import explain_local

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create deterministic evidence from an EVM transaction receipt.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--bundle", help="JSON file with transaction and receipt")
    source.add_argument("--hash", help="transaction hash to retrieve read-only")
    parser.add_argument("--rpc", help="explicit JSON-RPC endpoint for --hash")
    parser.add_argument("--ai-endpoint", help="optional loopback OpenAI-compatible endpoint")
    parser.add_argument("--ai-model", default="local-model")
    args = parser.parse_args(argv)
    try:
        if args.bundle:
            bundle = json.loads(Path(args.bundle).read_text(encoding="utf-8"))
            transaction, receipt = bundle["transaction"], bundle["receipt"]
        else:
            if not args.rpc:
                raise ValueError("--hash requires --rpc")
            transaction = rpc_call(args.rpc, "eth_getTransactionByHash", [args.hash])
            receipt = rpc_call(args.rpc, "eth_getTransactionReceipt", [args.hash])
            if not isinstance(transaction, dict) or not isinstance(receipt, dict):
                raise ValueError("transaction is pending or unknown")
        report = analyze_bundle(transaction, receipt)
        if args.ai_endpoint:
            report["ai_explanation"] = explain_local(report, args.ai_endpoint, args.ai_model)
            report["ai_disclaimer"] = "AI text is commentary; evidence fields remain authoritative."
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError, DecodeError) as exc:
        print(f"txreceiptai: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0
