"""Enhance reservations with approval and payment fields

Revision ID: 20260108_enhance_reservations
Revises: 8d08469a5c77
Create Date: 2026-01-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '20260108_enhance_reservations'
down_revision = '8d08469a5c77'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ========= 新增字段（SQLite 支持，直接 add_column） =========
    op.add_column('reservations', sa.Column('current_step', sa.String(50), nullable=True))

    op.add_column('reservations', sa.Column('approval_comment', sa.Text(), nullable=True))
    op.add_column('reservations', sa.Column('approval_time', sa.DateTime(timezone=True), nullable=True))

    op.add_column('reservations', sa.Column('advisor_id', sa.Integer(), nullable=True))
    op.add_column('reservations', sa.Column('advisor_comment', sa.Text(), nullable=True))
    op.add_column('reservations', sa.Column('advisor_approval_time', sa.DateTime(timezone=True), nullable=True))

    op.add_column('reservations', sa.Column('head_id', sa.Integer(), nullable=True))
    op.add_column('reservations', sa.Column('head_comment', sa.Text(), nullable=True))
    op.add_column('reservations', sa.Column('head_approval_time', sa.DateTime(timezone=True), nullable=True))

    op.add_column('reservations', sa.Column('payment_order_no', sa.String(64), nullable=True))
    op.add_column('reservations', sa.Column('payment_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reservations', sa.Column('refund_amount', sa.Float(), nullable=True))
    op.add_column('reservations', sa.Column('refund_time', sa.DateTime(timezone=True), nullable=True))

    op.add_column('reservations', sa.Column('borrow_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reservations', sa.Column('return_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reservations', sa.Column('handover_note', sa.Text(), nullable=True))
    op.add_column('reservations', sa.Column('return_note', sa.Text(), nullable=True))

    op.add_column(
        'reservations',
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )
    op.add_column(
        'reservations',
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    )

    # ========= 外键（SQLite 必须用 batch 模式） =========
    with op.batch_alter_table('reservations') as batch_op:
        batch_op.create_foreign_key(
            'fk_reservations_advisor_id',
            'users',
            ['advisor_id'],
            ['id']
        )
        batch_op.create_foreign_key(
            'fk_reservations_head_id',
            'users',
            ['head_id'],
            ['id']
        )


def downgrade() -> None:
    # ========= 先删外键（batch 模式） =========
    with op.batch_alter_table('reservations') as batch_op:
        batch_op.drop_constraint('fk_reservations_head_id', type_='foreignkey')
        batch_op.drop_constraint('fk_reservations_advisor_id', type_='foreignkey')

    # ========= 再删字段 =========
    op.drop_column('reservations', 'updated_at')
    op.drop_column('reservations', 'created_at')
    op.drop_column('reservations', 'return_note')
    op.drop_column('reservations', 'handover_note')
    op.drop_column('reservations', 'return_time')
    op.drop_column('reservations', 'borrow_time')
    op.drop_column('reservations', 'refund_time')
    op.drop_column('reservations', 'refund_amount')
    op.drop_column('reservations', 'payment_time')
    op.drop_column('reservations', 'payment_order_no')
    op.drop_column('reservations', 'head_approval_time')
    op.drop_column('reservations', 'head_comment')
    op.drop_column('reservations', 'head_id')
    op.drop_column('reservations', 'advisor_approval_time')
    op.drop_column('reservations', 'advisor_comment')
    op.drop_column('reservations', 'advisor_id')
    op.drop_column('reservations', 'approval_time')
    op.drop_column('reservations', 'approval_comment')
    op.drop_column('reservations', 'current_step')
