import os
import json
import requests

BASE_URL = "https://api.paystack.co"

def mode():
    return os.environ.get("PAYSTACK_MODE", "test")

def secret_key():
    return os.environ.get("PAYSTACK_SECRET_KEY", "")

def init_transaction(amount, email, metadata):
    if mode() != "live" or not secret_key():
        return {"authorization_url": "https://paystack.com/pay/test", "reference": f"TEST-{metadata.get('booking_id')}"}
    url = f"{BASE_URL}/transaction/initialize"
    headers = {"Authorization": f"Bearer {secret_key()}", "Content-Type": "application/json"}
    payload = {"amount": amount, "email": email, "metadata": metadata, "callback_url": metadata.get("callback_url")}
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=20)
    d = r.json()
    return {"authorization_url": d["data"]["authorization_url"], "reference": d["data"]["reference"]}

def verify_transaction(reference):
    if mode() != "live" or not secret_key():
        return {"status": "success", "amount": 5000}
    url = f"{BASE_URL}/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {secret_key()}"}
    r = requests.get(url, headers=headers, timeout=20)
    d = r.json()
    if d.get("data", {}).get("status") == "success":
        return {"status": "success", "amount": d["data"]["amount"]}
    return {"status": "failed", "amount": 0}
