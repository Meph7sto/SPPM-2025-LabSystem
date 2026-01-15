from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models.reservation import Reservation, ReservationStatus
from ..services.notifications import notify_overdue_reminder


def run_overdue_reminders(db: Session) -> int:
    """
    Find overdue borrowed reservations and send a single reminder.
    Returns the number of reminders sent.
    """
    now = datetime.now(timezone.utc)
    stmt = (
        select(Reservation)
        .where(Reservation.status == ReservationStatus.BORROWED)
        .where(Reservation.return_time.is_(None))
        .where(Reservation.end_time < func.now())
        .where(Reservation.overdue_notified_at.is_(None))
    )
    reservations = db.execute(stmt).scalars().all()

    for reservation in reservations:
        notify_overdue_reminder(
            db,
            to_user_id=reservation.user_id,
            reservation_id=reservation.id,
            due_time=reservation.end_time,
        )
        reservation.overdue_notified_at = now

    if reservations:
        db.commit()
    return len(reservations)


def main() -> None:
    db = SessionLocal()
    try:
        count = run_overdue_reminders(db)
        print(f"Overdue reminders sent: {count}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
