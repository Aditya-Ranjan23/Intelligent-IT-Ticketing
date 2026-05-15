"""Quick demo against the Python ML API."""
import json
import os
import sys
import urllib.request

BASE = os.environ.get("TICKET_API_URL", "http://127.0.0.1:8000")


def post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    cases = [
        {
            "name": "VPN (expect ml_complete or cache after seed)",
            "body": {
                "tenant_id": "demo",
                "text": "My VPN disconnects constantly when using AnyConnect.",
            },
        },
        {
            "name": "noisy unknown",
            "body": {"tenant_id": "demo", "text": "the thing is broken please help"},
        },
    ]
    print(f"Demo against {BASE}\n")
    for c in cases:
        print(f"--- {c['name']} ---")
        r = post("/tickets/resolve", c["body"])
        print(
            f"mode={r['resolution_mode']} class={r['classification']} "
            f"conf={r['confidence']:.3f} latency_ms={r['latency_ms']}"
        )
        if r.get("cache"):
            print("cache:", r["cache"])
        print("steps:", " | ".join(r["suggested_steps"][:2]))
        print()


if __name__ == "__main__":
    main()
