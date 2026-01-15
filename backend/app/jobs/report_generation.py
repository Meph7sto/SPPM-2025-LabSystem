import sys
import os
from datetime import date

# Add parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import SessionLocal
from app.services.report_service import generate_and_save_report
from app.models.report import ReportType

def run_periodic_reports():
    db = SessionLocal()
    try:
        today = date.today()
        
        # 1. Check if it's Monday (generate weekly report for last week)
        # Actually, the requirement says "by cycle", usually we generate current snapshot or last period.
        # For simplicity and demonstration, we'll just generate them if called.
        
        print(f"[{today}] Running periodic report generation...")
        
        # Weekly
        if today.weekday() == 0: # Monday
            print("Generating weekly report...")
            generate_and_save_report(db, ReportType.WEEKLY)
            
        # Monthly
        if today.day == 1: # 1st of month
            print("Generating monthly report...")
            generate_and_save_report(db, ReportType.MONTHLY)
            
        # Yearly
        if today.month == 1 and today.day == 1: # Jan 1st
            print("Generating yearly report...")
            generate_and_save_report(db, ReportType.YEARLY)
            
        print("Done.")
    except Exception as e:
        print(f"Error generating reports: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_periodic_reports()
