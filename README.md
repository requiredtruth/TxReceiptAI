# TxReceiptAI

TxReceiptAI turns an EVM transaction plus its receipt into a small, deterministic evidence report. It calculates the exact receipt fee, checks transaction/receipt consistency, reports success or revert status, and decodes four common fixed ABI calls without guessing contract identity.

The core analyzer is offline and dependency-free. A read-only JSON-RPC fetch mode is available, and an optional explanation can be requested from a **loopback-only** OpenAI-compatible server. AI prose is commentary; the structured evidence remains authoritative.

## Why this exists

Block explorers are useful, but audit notes and bug reports often need portable evidence that can be regenerated. TxReceiptAI focuses on that narrow job:

- no wallet connection, signing, approvals, transaction submission, trading, or custody;
- exact integer arithmetic for gas fees;
- strict transaction hash, address, quantity, ABI-word, and receipt checks;
- explicit unknowns instead of inferred token symbols, prices, identities, intent, or safety;
- stable JSON output suitable for diffs and downstream tests.

## Install and run

Python 3.11 or newer is required. The package has no runtime dependencies.

```bash
python -m txreceiptai --bundle examples/bundle.json
```

Fetch a confirmed transaction from an endpoint you explicitly choose:

```bash
python -m txreceiptai \
  --hash 0xYOUR_32_BYTE_TRANSACTION_HASH \
  --rpc https://YOUR_READ_ONLY_RPC_ENDPOINT
```

Add bounded local-model commentary:

```bash
python -m txreceiptai \
  --bundle examples/bundle.json \
  --ai-endpoint http://127.0.0.1:8080 \
  --ai-model your-local-model
```

The AI endpoint must resolve syntactically to `localhost`, `127.0.0.1`, or `::1`. Only the already-derived report is sent to it.

## Deterministic coverage

The first release recognizes only these exact selectors:

- `transfer(address,uint256)`
- `approve(address,uint256)`
- `transferFrom(address,address,uint256)`
- `setApprovalForAll(address,bool)`

Everything else is labeled `unknown` with its selector and byte length. TxReceiptAI does not fetch ABIs, resolve proxies, decode logs, identify contracts, or decide whether an interaction was authorized or safe.

## Test

```bash
python -m unittest discover -s tests -v
python -m compileall -q txreceiptai tests
```

## Support development

Donations fund additional production. A donor may open the funded-direction issue template with the asset, network, public transaction hash, and requested direction. See [SUPPORT.md](SUPPORT.md) for the attribution and safety rules.

## License

Apache-2.0. See [LICENSE](LICENSE).


## Install and run

```sh
chmod +x install.sh run.sh
./install.sh
./run.sh --help
```


## Standard launcher

`./run.sh` is the normal entry point. It runs `./install.sh` automatically when setup is missing, then opens the PySide6 control panel with live output and actions for the demo, tests, repair, and stop. Use `./cli.sh` for CLI-only operation.
