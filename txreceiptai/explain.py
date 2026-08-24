from __future__ import annotations
import json
from urllib import parse, request

def explain_local(report: dict[str, object], endpoint: str, model: str, *, timeout: float = 60.0) -> str:
    parsed = parse.urlparse(endpoint)
    if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("AI explanations are restricted to a loopback endpoint")
    url = endpoint.rstrip("/")
    if not url.endswith("/chat/completions"):
        url += "/v1/chat/completions"
    prompt = "Explain these deterministic EVM receipt facts in plain language. Do not infer identity, intent, safety, token price, or authorization. Separate facts from unknowns.\n" + json.dumps(report, sort_keys=True)
    body = json.dumps({"model":model,"temperature":0,"messages":[{"role":"user","content":prompt}]}).encode()
    req = request.Request(url, data=body, headers={"Content-Type":"application/json"})
    with request.urlopen(req, timeout=timeout) as response:
        payload = json.load(response)
    try:
        return payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("local AI endpoint returned no explanation") from exc
