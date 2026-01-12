"""Finance integration tables and voucher field

Revision ID: 20260112_finance_integration
Revises: 20260108_enhance_reservations
Create Date: 2026-01-12

"""

from alembic import op
import sqlalchemy as sa


revision = "20260112_finance_integration"
down_revision = "20260108_enhance_reservations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) 预约表：增加凭证引用字段
    op.add_column("reservations", sa.Column("payment_voucher_ref", sa.String(length=255), nullable=True))

    # 2) 财务支付单表（对接/Mock 用）
    op.create_table(
        "finance_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_no", sa.String(length=64), nullable=False),
        sa.Column("reservation_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("paid_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["reservation_id"], ["reservations.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_finance_payments_order_no"), "finance_payments", ["order_no"], unique=True)
    op.create_index(op.f("ix_finance_payments_reservation_id"), "finance_payments", ["reservation_id"], unique=True)

    # 3) 退款记录表
    op.create_table(
        "refund_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reservation_id", sa.Integer(), nullable=False),
        sa.Column("order_no", sa.String(length=64), nullable=True),
        sa.Column("original_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("refund_rate", sa.Float(), nullable=False, server_default="0.95"),
        sa.Column("refund_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="processed"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["reservation_id"], ["reservations.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_refund_records_reservation_id"), "refund_records", ["reservation_id"], unique=False)

    # 4) 兼容历史迁移：将旧的枚举大写值转换为当前代码的小写字符串。
    #    由于 sqlite 上修改 Enum CHECK 约束困难，这里做一次数据层面的映射，后续由 ORM 写入小写值。
    #    若历史数据库不存在这些值，UPDATE 不会影响行。
    op.execute(
        "UPDATE reservations SET status='pending' WHERE status IN ('PENDING')"
    )
    op.execute(
        "UPDATE reservations SET status='approved' WHERE status IN ('APPROVED')"
    )
    op.execute(
        "UPDATE reservations SET status='rejected' WHERE status IN ('REJECTED')"
    )
    op.execute(
        "UPDATE reservations SET status='completed' WHERE status IN ('COMPLETED')"
    )
    op.execute(
        "UPDATE reservations SET status='cancelled' WHERE status IN ('CANCELLED')"
    )

    op.execute(
        "UPDATE reservations SET payment_status='pending' WHERE payment_status IN ('PENDING')"
    )
    op.execute(
        "UPDATE reservations SET payment_status='paid' WHERE payment_status IN ('PAID')"
    )
    op.execute(
        "UPDATE reservations SET payment_status='waived' WHERE payment_status IN ('WAIVED')"
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_refund_records_reservation_id"), table_name="refund_records")
    op.drop_table("refund_records")

    op.drop_index(op.f("ix_finance_payments_reservation_id"), table_name="finance_payments")
    op.drop_index(op.f("ix_finance_payments_order_no"), table_name="finance_payments")
    op.drop_table("finance_payments")

    op.drop_column("reservations", "payment_voucher_ref")
