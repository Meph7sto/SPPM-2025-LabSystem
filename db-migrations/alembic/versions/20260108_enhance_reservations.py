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
    # 添加预约表的新字段
    with op.batch_alter_table('reservations') as batch_op:
        # 当前审批步骤
        batch_op.add_column(sa.Column('current_step', sa.String(50), nullable=True))
        
        # 审批意见和时间
        batch_op.add_column(sa.Column('approval_comment', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('approval_time', sa.DateTime(timezone=True), nullable=True))
        
        # 导师审批（学生申请）
        batch_op.add_column(sa.Column('advisor_id', sa.Integer(), sa.ForeignKey('users.id', name='fk_reservations_advisor_id'), nullable=True))
        batch_op.add_column(sa.Column('advisor_comment', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('advisor_approval_time', sa.DateTime(timezone=True), nullable=True))
        
        # 负责人审批（校外申请）
        batch_op.add_column(sa.Column('head_id', sa.Integer(), sa.ForeignKey('users.id', name='fk_reservations_head_id'), nullable=True))
        batch_op.add_column(sa.Column('head_comment', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('head_approval_time', sa.DateTime(timezone=True), nullable=True))
        
        # 支付信息
        batch_op.add_column(sa.Column('payment_order_no', sa.String(64), nullable=True))
        batch_op.add_column(sa.Column('payment_time', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('refund_amount', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('refund_time', sa.DateTime(timezone=True), nullable=True))
        
        # 借出/归还信息
        batch_op.add_column(sa.Column('borrow_time', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('return_time', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('handover_note', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('return_note', sa.Text(), nullable=True))
        
        # 时间戳
        batch_op.add_column(sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('reservations') as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('return_note')
        batch_op.drop_column('handover_note')
        batch_op.drop_column('return_time')
        batch_op.drop_column('borrow_time')
        batch_op.drop_column('refund_time')
        batch_op.drop_column('refund_amount')
        batch_op.drop_column('payment_time')
        batch_op.drop_column('payment_order_no')
        batch_op.drop_column('head_approval_time')
        batch_op.drop_column('head_comment')
        batch_op.drop_column('head_id')
        batch_op.drop_column('advisor_approval_time')
        batch_op.drop_column('advisor_comment')
        batch_op.drop_column('advisor_id')
        batch_op.drop_column('approval_time')
        batch_op.drop_column('approval_comment')
        batch_op.drop_column('current_step')
