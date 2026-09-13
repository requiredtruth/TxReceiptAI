# Changelog

## 0.1.1 - 2026-09-13

- Itemize execution and EIP-4844 blob fees and report their exact transaction total.
- Reject receipts with only one of `blobGasUsed` or `blobGasPrice`.
- Wire the desktop demo and test actions to real, CI-covered workflows.

## 0.1.0 - 2026-08-24

- Add deterministic transaction and receipt consistency checks.
- Calculate exact gas fees from receipt quantities.
- Decode four fixed, common EVM calldata signatures with strict ABI validation.
- Add read-only JSON-RPC retrieval and optional loopback-only AI commentary.
- Document explicit non-custodial scope and unknowns.
