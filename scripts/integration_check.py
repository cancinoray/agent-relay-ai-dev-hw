"""Integration test: the Question 2 task flow against a running API.

Usage: BASE_URL=http://127.0.0.1:8000 python scripts/integration_check.py
"""

import json
import os
import sys
import urllib.request

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


def call(method, path, token=None, body=None):
    req = urllib.request.Request(
        BASE_URL + path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,
        headers={"content-type": "application/json"},
    )
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode()
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        return exc.code, json.loads(raw) if raw else None


def main() -> int:
    s, alice = call("POST", "/api/v1/agents", body={"name": "alice"})
    assert s == 201, alice
    s, bob = call("POST", "/api/v1/agents", body={"name": "uppercase"})
    assert s == 201, bob

    s, task = call(
        "POST",
        "/api/v1/tasks",
        token=alice["token"],
        body={"to": bob["agent_id"], "input": "hello relay"},
    )
    assert s == 201 and task["status"] == "queued", task

    s, claim = call(
        "POST",
        "/api/v1/tasks/claim",
        token=bob["token"],
        body={"worker_id": "ci-check", "wait_seconds": 5},
    )
    assert s == 200 and claim["task_id"] == task["task_id"], claim

    tid = task["task_id"]
    s, done = call(
        "POST",
        f"/api/v1/tasks/{tid}/complete",
        token=bob["token"],
        body={"claim_token": claim["claim_token"], "output": "HELLO RELAY"},
    )
    assert s == 200 and done["status"] == "completed", done

    s, seen = call("GET", f"/api/v1/tasks/{tid}", token=alice["token"])
    assert s == 200 and seen["status"] == "completed" and seen["output"] == "HELLO RELAY", seen

    print(f"integration OK: {tid} completed, output={seen['output']!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
