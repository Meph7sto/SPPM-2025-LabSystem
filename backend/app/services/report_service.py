import os
from datetime import datetime, date, timedelta
from io import BytesIO
from openpyxl import Workbook
from sqlalchemy.orm import Session
from ..models.reservation import Reservation
from ..models.report import GeneratedReport, ReportType
from ..core.config import settings

# Ensure storage directory exists
REPORTS_DIR = os.path.join(os.getcwd(), "storage", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_and_save_report(db: Session, report_type: ReportType, user_id: int = None) -> GeneratedReport:
    today = date.today()
    
    if report_type == ReportType.WEEKLY:
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        period_label = f"{today.year}-W{today.isocalendar()[1]}"
        filename_prefix = "weekly_report"
    elif report_type == ReportType.MONTHLY:
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        period_label = f"{today.year}-{today.month:02d}"
        filename_prefix = "monthly_report"
    elif report_type == ReportType.YEARLY:
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
        period_label = f"{today.year}"
        filename_prefix = "yearly_report"
    else:
        raise ValueError("Invalid report type")

    # Query reservations for the period
    # Note: Using created_at or start_time? The original code used created_at for ranges.
    reservations = (
        db.query(Reservation)
        .filter(Reservation.created_at >= start_date)
        .filter(Reservation.created_at <= datetime.combine(end_date, datetime.max.time()))
        .all()
    )

    # Create Excel
    wb = Workbook()
    ws = wb.active
    ws.title = report_type.value.capitalize()

    # Table Header
    headers = ["ID", "Device ID", "User ID", "Start Time", "End Time", "Status", "Payment Status", "Amount"]
    ws.append(headers)

    # Data rows
    for r in reservations:
        ws.append([
            r.id,
            r.device_id,
            r.user_id,
            r.start_time.isoformat() if r.start_time else "",
            r.end_time.isoformat() if r.end_time else "",
            r.status,
            r.payment_status,
            float(r.payment_amount) if r.payment_amount else 0.0,
        ])

    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{period_label}_{timestamp}.xlsx"
    file_path = os.path.join(REPORTS_DIR, filename)
    wb.save(file_path)

    # Record in database
    report = GeneratedReport(
        report_type=report_type,
        period_start=datetime.combine(start_date, datetime.min.time()),
        period_end=datetime.combine(end_date, datetime.max.time()),
        file_path=file_path,
        filename=filename,
        generated_by_id=user_id
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return report
