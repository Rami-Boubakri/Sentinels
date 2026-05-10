"""
Sentinels — Demo Test Scenarios for Judges
==========================================
Run this from the backend directory:
  .\\venv\\Scripts\\python.exe test_scenarios.py

Each scenario fires a real event into the live system (POST /api/v1/inputs/).
The live UI at http://localhost:3000 will show the agents working in real time.
"""

import urllib.request
import json
import time
import sys

API_URL = "http://127.0.0.1:8000/api/v1/inputs/"

SCENARIOS = [
    # ─────────────────────────────────────────────────────────────────────────
    # SCENARIO 1: Classic Early Warning — Large GGEI Corporate (XYZ Industries)
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "SCENARIO 1 - Early Warning: XYZ Industries SA (Textile Corporate)",
        "description": "A large GGEI-portfolio textile company shows 3 classic NPL precursors: missed installments, turnover decline, and sector stress.",
        "payload": {
            "source": "demo",
            "payload": {
                "customer_id": "CUST-XYZ-001",
                "event_type": "early_warning",
                "details": (
                    "Direction Régionale Sfax flags borrower XYZ Industries SA - a textile corporate in the GGEI portfolio. "
                    "Outstanding loan: TND 12M. Situation: 2 missed installments at 45 DPD, account turnover down 35% over "
                    "6 months, late filing of audited financial statements (Q3 overdue by 60 days), key buyer (export to Italy) "
                    "has cancelled order worth TND 2M. Sector context: Tunisian textile sector under macro stress due to EU tariff "
                    "changes. Local competitor (Sfax Textile SA) declared bankruptcy last month. Borrower currently at IFRS 9 Stage 1 "
                    "but exhibits multiple Stage 2 migration triggers per BCT Circulaire 91-24 criteria."
                )
            }
        }
    },

    # ─────────────────────────────────────────────────────────────────────────
    # SCENARIO 2: Outright Default — Logistics Group
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "SCENARIO 2 - Default Event: Samir Logistics Group (Transport Sector)",
        "description": "A logistics company has just hit formal default status. Triggers the Recovery + Risk + Guarantees departments.",
        "payload": {
            "source": "demo",
            "payload": {
                "customer_id": "CUST-SAM-003",
                "event_type": "default",
                "details": (
                    "Samir Logistics Group has formally defaulted on loan TND 8.5M (exposure date: 2023-06). "
                    "Current DPD: 127 days. No installment paid in 4 months. Account shows near-zero operational inflows. "
                    "Owner is reachable but uncooperative — rejected restructuring proposal in March 2025. "
                    "Collateral: 3 commercial trucks (estimated current market value TND 1.8M) + 1 warehouse in Tunis (TND 3.5M). "
                    "Collateral coverage ratio: 62.4% — below the 80% BCT minimum. "
                    "Legal action: preliminary notice served 30 days ago. Judicial recovery pathway being considered. "
                    "Sector note: fuel price surge (+22% YoY) has severely compressed margins across Tunisian transport sector."
                )
            }
        }
    },

    # ─────────────────────────────────────────────────────────────────────────
    # SCENARIO 3: Regulatory Inquiry — BCT Circular Compliance
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "SCENARIO 3 - Regulatory: BCT Circular 2025-04 Compliance Review",
        "description": "New BCT circular just dropped. System checks all active GGEI loans for compliance impact.",
        "payload": {
            "source": "demo",
            "payload": {
                "customer_id": "CUST-BAC-004",
                "event_type": "regulatory_inquiry",
                "details": (
                    "BCT has issued Circular 2025-04 on 08-May-2025 updating provisioning rules for Stage 2 loans in the real "
                    "estate and construction sector. New rule: minimum ECL provision floor of 15% for all construction loans "
                    "above TND 10M where DPD > 0 or where sector concentration risk exceeds 20% of bank portfolio. "
                    "Ben Ali Construction SA (loan TND 22M, currently Stage 1, DPD 0) must be reviewed for pre-emptive "
                    "reclassification. The bank's construction sector concentration is currently 18.7% — approaching the threshold. "
                    "The circular takes effect 60 days from issuance (08-July-2025). "
                    "Action required: legal analysis, provisioning recalculation, and BCT reporting update."
                )
            }
        }
    },

    # ─────────────────────────────────────────────────────────────────────────
    # SCENARIO 4: DORA / Anomaly Alert — Behavioral Anomaly Detected
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "SCENARIO 4 - Anomaly Alert: Green Future Energy SA (Behavioral Red Flags)",
        "description": "Data analytics engine flags unusual behavioral patterns on a renewable energy loan.",
        "payload": {
            "source": "demo",
            "payload": {
                "customer_id": "CUST-GFE-006",
                "event_type": "early_warning",
                "details": (
                    "Direction Données Analytiques has flagged Green Future Energy SA for a cluster of behavioral anomalies "
                    "detected by the bank's automated monitoring system. Anomalies detected over last 90 days: "
                    "(1) 7 large cash withdrawals totalling TND 920K — unusual for a B2B energy company; "
                    "(2) Revenue inflows from main off-taker (STEG — Tunisian electricity utility) delayed by 45 days with "
                    "no official communication; "
                    "(3) Loan TND 15M now at DPD 18 — first delay in 24-month relationship history; "
                    "(4) Key account signatories changed (2 of 3 directors replaced in March 2025 per company registry); "
                    "(5) Pattern matches 3 historical NPL cases from 2021-2022 cohort analysis. "
                    "Current IFRS 9 Stage: 1. Immediate Stage 2 watch-list classification recommended pending investigation."
                )
            }
        }
    },

    # ─────────────────────────────────────────────────────────────────────────
    # SCENARIO 5: SME Customer Complaint — TPME Sector
    # ─────────────────────────────────────────────────────────────────────────
    {
        "name": "SCENARIO 5 - Customer Case: Optima Retail Group (SME Distress)",
        "description": "An SME retail company reaches out about restructuring. System routes to relevant departments.",
        "payload": {
            "source": "demo",
            "payload": {
                "customer_id": "CUST-OPT-007",
                "event_type": "early_warning",
                "details": (
                    "Optima Retail Group (SME, TPME segment, loan TND 1.2M) has proactively contacted STB requesting a "
                    "voluntary restructuring of their loan before entering delinquency. Company context: "
                    "operates 4 retail outlets in Sfax medina. Revenue dropped 28% post-COVID recovery stall and due to "
                    "new competing mall opening nearby. Current DPD: 0 (customer is proactive). "
                    "Request: 6-month principal moratorium + interest rate reduction from 9.5% to 7.5%. "
                    "Financial docs submitted: latest balance sheet shows equity still positive (TND 340K) but cash flow "
                    "is negative for last 2 quarters. Guarantees: personal guarantee from owner + stock pledge (TND 280K). "
                    "Branch manager (Dir. Régionale Sfax) recommends the restructuring as the owner is cooperative and "
                    "sector recovery likely within 12-18 months."
                )
            }
        }
    },
]


def post_scenario(scenario: dict) -> dict:
    data = json.dumps(scenario["payload"]).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def run_all():
    print("\n" + "=" * 80)
    print("  SENTINELS - DEMO SCENARIO RUNNER")
    print("  STB Bank Multi-Agent NPL Management System")
    print("=" * 80)
    print(f"\n  Backend:  http://127.0.0.1:8000")
    print(f"  Frontend: http://localhost:3000")
    print(f"  Open the frontend to watch agents work in real-time!\n")

    for i, scenario in enumerate(SCENARIOS):
        print(f"\n{'*'*80}")
        print(f"  {scenario['name']}")
        print(f"  {scenario['description']}")
        print(f"{'*'*80}")

        try:
            result = post_scenario(scenario)
            ticket_id = result.get("ticket_id")
            print(f"  [OK] Accepted! Ticket ID: {ticket_id}")
            print(f"  Live view: http://localhost:3000/tickets/{ticket_id}")
        except Exception as e:
            print(f"  [ERROR] Error: {e}")

        # Wait between scenarios so agents don't overlap too much
        if i < len(SCENARIOS) - 1:
            delay = 5
            print(f"\n  Wait {delay}s before next scenario...")
            time.sleep(delay)

    print(f"\n{'=' * 80}")
    print("  All scenarios fired! Check http://localhost:3000/tickets for all tickets.")
    print(f"{'=' * 80}\n")


def run_single(index: int):
    scenario = SCENARIOS[index]
    print(f"\n  Running: {scenario['name']}")
    try:
        result = post_scenario(scenario)
        ticket_id = result.get("ticket_id")
        print(f"  [OK] Ticket ID: {ticket_id}")
        print(f"  Link: http://localhost:3000/tickets/{ticket_id}")
    except Exception as e:
        print(f"  [ERROR] Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            idx = int(sys.argv[1]) - 1
            if 0 <= idx < len(SCENARIOS):
                run_single(idx)
            else:
                print(f"Scenario index must be 1–{len(SCENARIOS)}")
        except ValueError:
            print("Usage: python test_scenarios.py [scenario_number 1-5]")
    else:
        run_all()
