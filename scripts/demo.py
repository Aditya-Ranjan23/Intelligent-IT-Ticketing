"""
Interactive demo script for v0.2.0 Python API.
Tests fast-path classification, OCR screenshot parsing, deep resolution polling, and Redis cache hit.
"""
import base64
import os
import time
import httpx

BASE_URL = os.environ.get("TICKET_API_URL", "http://127.0.0.1:8000")


def run_demo():
    print(f"Connecting to API at {BASE_URL}...\n")
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)

    # Health check
    try:
        r = client.get("/health")
        print(f"Service Health Check: {r.json()}\n")
    except Exception as e:
        print(f"Could not connect to API at {BASE_URL}: {e}")
        print("Please start the API server in another terminal: python -m uvicorn app.main:app --port 8000")
        return

    test_cases = [
        {
            "name": "1. High-Confidence VPN Fast Path",
            "body": {
                "tenantId": "demo-tenant-1",
                "text": "My Cisco AnyConnect VPN disconnects constantly when connected on Wi-Fi.",
            },
        },
        {
            "name": "2. High-Confidence Outlook Sync",
            "body": {
                "tenantId": "demo-tenant-1",
                "text": "Outlook client disconnected error in status bar and mailbox not updating.",
            },
        },
        {
            "name": "3. Screenshot Ticket with Base64 Payload",
            "body": {
                "tenantId": "demo-tenant-1",
                "text": "Error message displayed on screen when launching Teams.",
                "imageBase64": base64.b64encode(b"fake-demo-png-image-content-bytes-for-ocr-test").decode("utf-8"),
            },
        },
        {
            "name": "4. Noisy / Unknown Issue (Escalates to Deep RAG Resolution)",
            "body": {
                "tenantId": "demo-tenant-1",
                "text": "The custom ERP legacy system throws database deadlock exception error code 0x88293.",
                "logSnippet": "CRITICAL 2026-07-27 10:42:19 db_connection_pool.py:91 - Deadlock detected on transaction ID 0x88293.",
            },
        },
        {
            "name": "5. Cache Hit Test (Re-submitting Case 1)",
            "body": {
                "tenantId": "demo-tenant-1",
                "text": "My Cisco AnyConnect VPN disconnects constantly when connected on Wi-Fi.",
            },
        },
    ]

    for tc in test_cases:
        print(f"--- {tc['name']} ---")
        t0 = time.perf_counter()
        resp = client.post("/tickets/resolve", json=tc["body"])
        wall_ms = round((time.perf_counter() - t0) * 1000)

        if resp.status_code != 200:
            print(f"Error HTTP {resp.status_code}: {resp.text}\n")
            continue

        data = resp.json()
        print(
            f"Mode: {data['resolution_mode']:<15} | Category: {data['classification']:<20} | "
            f"Conf: {data['confidence']:.2f} | Latency: {data['latency_ms']}ms (wall: {wall_ms}ms)"
        )
        print("Suggested Steps:", " | ".join(data["suggested_steps"][:2]))

        if data.get("ocr_text"):
            print(f"OCR Extracted: {data['ocr_text']}")

        if data.get("ticket_id") and data["resolution_mode"] == "ml_needs_deep":
            ticket_id = data["ticket_id"]
            print(f"Polling async deep resolution for ticket ID '{ticket_id}'...")
            
            for _ in range(10):
                time.sleep(1.0)
                st_resp = client.get(f"/tickets/{ticket_id}/status")
                if st_resp.status_code == 200:
                    st_data = st_resp.json()
                    if st_data["status"] in ("deep_resolution_finished", "deep_resolution_error"):
                        print(f"Final Async Status: {st_data['status']}")
                        if st_data.get("deep_result_text"):
                            print(f"Deep Resolution Text:\n{st_data['deep_result_text']}")
                        break
        print()


if __name__ == "__main__":
    run_demo()
