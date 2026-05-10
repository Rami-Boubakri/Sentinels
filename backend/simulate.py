import sys
import os
import json

# Ensure app module can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

from app.database import SessionLocal
from app.orchestrator.orchestrator import process_new_event
from app.models.report import Report
from app.models.user import User

def run_simulation():
    db = SessionLocal()
    
    payload = {
        "customer_id": "CUST-XYZ-001",
        "event_type": "early_warning",
        "details": "Direction Regionale Sfax flags borrower XYZ Industries SA - a textile corporate (GGEI portfolio, outstanding loan TND 12M, 2 missed installments at 45 dpd, account turnover down 35% over 6 months, late filing of audited statements, sector under stress)."
    }
    
    print("\n" + "="*80)
    print("1. INPUT RECEIVED:")
    print("="*80)
    print(json.dumps(payload, indent=2))
    
    print("\n" + "="*80)
    print("2 & 3. ORCHESTRATOR PROCESSING (Routing & Agent Execution)...")
    print("="*80)
    
    try:
        # Run orchestrator
        ticket = process_new_event(db, payload)
        
        print(f"Ticket Created: ID {ticket.id}, Customer: {ticket.customer_id}")
        
        # Fetch reports
        reports = db.query(Report).filter(Report.ticket_id == ticket.id).all()
        
        print("\n" + "="*80)
        print(f"4. DEPARTMENT AGENT ANALYSIS RESULTS (Found {len(reports)} reports):")
        print("="*80)
        
        for report in reports:
            print(f"\n[{report.department_id} Agent Analysis]")
            print("-" * 50)
            try:
                # Content should be a JSON dict from the LLM
                content = report.content
                if isinstance(content, str):
                    content = json.loads(content)
                    
                print(f"Analysis: {content.get('analysis', '')}")
                print(f"Proposed Action: {content.get('proposed_action', '')}")
                print(f"Confidence: {content.get('confidence', '')}")
            except Exception as e:
                print("Raw Content:", report.content)
            
            print("-" * 50)
            
    except Exception as e:
        print(f"Error during simulation: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_simulation()
