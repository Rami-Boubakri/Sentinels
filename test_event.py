import urllib.request
import json

payload = {
    "source": "demo",
    "payload": {
        "customer_id": "CUST-XYZ-001",
        "event_type": "early_warning",
        "details": "Direction Regionale Sfax flags borrower XYZ Industries SA - a textile corporate (GGEI portfolio, outstanding loan TND 12M, 2 missed installments at 45 dpd, account turnover down 35% over 6 months, late filing of audited statements, sector under stress)."
    }
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request("http://127.0.0.1:8000/api/v1/inputs/", data=data, headers={'Content-Type': 'application/json'})

print("Submitting XYZ Industries Early Warning Event...")
try:
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.status}")
        print(f"Response: {response.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
