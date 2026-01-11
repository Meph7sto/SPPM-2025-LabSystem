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
    
    # 当前审批步骤
    op.add_column('reservations', sa.Column('current_step', sa.String(50), nullable=True))
    
    # 审批意见和时间
    op.add_column('reservations', sa.Column('approval_comment', sa.Text(), nullable=True))
    op.add_column('reservations', sa.Column('approval_time', sa.DateTime(timezone=True), nullable=True))
    
    # 导师审批（学生申请）
    op.add_column('reservations', sa.Column('advisor_id', sa.Integer(), nullable=True))
    op.add_column('reservations', sa.Column('advisor_comment', sa.Text(), nullable=True))
    op.add_column('reservations', sa.Column('advisor_approval_time', sa.DateTime(timezone=True), nullable=True))
    
    # 负责人审批（校外申请）
    op.add_column('reservations', sa.Column('head_id', sa.Integer(), nullable=True))
    op.add_column('reservations', sa.Column('head_comment', sa.Text(), nullable=True))
    op.add_column('reservations', sa.Column('head_approval_time', sa.DateTime(timezone=True), nullable=True))
    
    # 支付信息
    op.add_column('reservations', sa.Column('payment_order_no', sa.String(64), nullable=True))
    op.add_column('reservations', sa.Column('payment_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reservations', sa.Column('refund_amount', sa.Float(), nullable=True))
    op.add_column('reservations', sa.Column('refund_time', sa.DateTime(timezone=True), nullable=True))

    # 借出/归还信息
    op.add_column('reservations', sa.Column('borrow_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reservations', sa.Column('return_time', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reservations', sa.Column('handover_note', sa.Text(), nullable=True))
    op.add_column('reservations', sa.Column('return_note', sa.Text(), nullable=True))
    
    # 时间戳
    op.add_column('reservations', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.add_column('reservations', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    
    # 添加外键约束
    op.create_foreign_key('fk_reservations_advisor_id', 'reservations', 'users', ['advisor_id'], ['id'])
    op.create_foreign_key('fk_reservations_head_id', 'reservations', 'users', ['head_id'], ['id'])
    
    # 更新payment_status的默认值（从PENDING改为NOT_REQUIRED）
    # 因为校内人员不需要支付
    # 这里我们只是添加说明，实际修改enum需要更复杂的操作


def downgrade() -> None:
    # 删除外键约束
    op.drop_constraint('fk_reservations_head_id', 'reservations', type_='foreignkey')
    op.drop_constraint('fk_reservations_advisor_id', 'reservations', type_='foreignkey')
    
    # 删除新增字段
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
