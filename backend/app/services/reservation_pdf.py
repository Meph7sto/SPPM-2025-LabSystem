from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from fpdf import FPDF

from ..core.errors import AppError, ErrorCode
from ..models.reservation import Reservation
from ..models.user import BorrowerType

FONT_CANDIDATES: Iterable[Path] = [
    Path("C:/Windows/Fonts/simhei.ttf"), # SimHei (Windows) - 优先使用.ttf而不是.ttc
    Path("C:/Windows/Fonts/simsun.ttc"), # SimSun (Windows)
    Path("C:/Windows/Fonts/msyh.ttc"),   # Microsoft YaHei (Windows)
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"),
]


def _pick_font() -> Optional[Path]:
    for path in FONT_CANDIDATES:
        if path.exists():
            return path
    return None


def _fmt_dt(dt) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else "-"


def _safe_text(text: str, use_unicode: bool) -> str:
    if use_unicode:
        return text
    # 非 unicode 模式下用 latin-1 回退，避免报错
    return text.encode("latin-1", "replace").decode("latin-1")


def _kv(pdf: FPDF, label: str, value: str, font: str, use_unicode: bool) -> None:
    """输出键值对，使用简单的cell布局避免multi_cell的问题"""
    pdf.set_font(font, "", 11)
    label_text = _safe_text(label, use_unicode)
    value_text = _safe_text(value, use_unicode)
    
    # 使用cell而不是multi_cell，确保内容在左侧单列显示
    # 如果文本太长，截断后添加省略号
    max_length = 80  # 最大字符数
    full_text = f"{label_text}{value_text}"
    
    if len(full_text) > max_length:
        full_text = full_text[:max_length] + "..."
    
    pdf.cell(0, 8, full_text, ln=1)


def _borrower_label(reservation: Reservation) -> str:
    bt = reservation.user.borrower_type if reservation.user else None
    mapping = {
        BorrowerType.STUDENT: "学生",
        BorrowerType.TEACHER: "教师",
        BorrowerType.EXTERNAL: "校外",
    }
    return mapping.get(bt, "未知")


def _status_label(status) -> str:
    """将预约状态枚举转换为中文"""
    from ..models.reservation import ReservationStatus
    mapping = {
        ReservationStatus.PENDING: "待审批",
        ReservationStatus.ADVISOR_APPROVED: "导师已审批",
        ReservationStatus.ADMIN_APPROVED: "管理员已审批",
        ReservationStatus.HEAD_APPROVED: "负责人已审批",
        ReservationStatus.APPROVED: "审批通过",
        ReservationStatus.REJECTED: "已驳回",
        ReservationStatus.RETURNED: "已退回",
        ReservationStatus.EFFECTIVE: "已生效",
        ReservationStatus.BORROWED: "已借出",
        ReservationStatus.COMPLETED: "已完成",
        ReservationStatus.CANCELLED: "已取消",
    }
    return mapping.get(status, str(status))


def _step_label(step) -> str:
    """将审批步骤枚举转换为中文"""
    from ..models.reservation import ApprovalStep
    if step is None:
        return "-"
    mapping = {
        ApprovalStep.ADVISOR: "导师审批",
        ApprovalStep.ADMIN: "管理员审批",
        ApprovalStep.HEAD: "负责人审批",
        ApprovalStep.PAYMENT: "缴费确认",
        ApprovalStep.FINAL: "最终确认",
    }
    return mapping.get(step, str(step))


def _payment_status_label(status) -> str:
    """将支付状态枚举转换为中文"""
    from ..models.reservation import PaymentStatus
    mapping = {
        PaymentStatus.NOT_REQUIRED: "无需支付",
        PaymentStatus.PENDING: "待支付",
        PaymentStatus.PAID: "已支付",
        PaymentStatus.REFUNDED: "已退款",
        PaymentStatus.WAIVED: "已免除",
    }
    return mapping.get(status, str(status))


def generate_reservation_pdf(reservation: Reservation) -> bytes:
    """
    生成预约单 PDF，覆盖学生/教师/校外三类场景。
    """
    # 尝试查找支持中文的Unicode字体
    font_path = _pick_font()
    use_unicode = font_path is not None
    font_name = "CustomFont" if use_unicode else "Helvetica"

    # 明确指定单位(mm)和页面格式(A4)
    pdf = FPDF(unit='mm', format='A4')
    
    # 如果找到了Unicode字体，添加到PDF中
    if use_unicode and font_path:
        try:
            pdf.add_font("CustomFont", "", str(font_path), uni=True)
        except Exception:
            # 字体加载失败，回退到Helvetica
            use_unicode = False
            font_name = "Helvetica"
    # 设置合理的页面边距（必须在add_page之前）
    # 左侧对齐布局，增加右边距防止文字超出页面
    pdf.set_margins(left=20, top=15, right=25)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # 标题
    pdf.set_font(font_name, "", 16)
    pdf.cell(0, 12, _safe_text("实验设备预约单", use_unicode), ln=1)

    pdf.set_font(font_name, "", 11)
    pdf.cell(0, 8, _safe_text(f"预约编号：R-{reservation.id}", use_unicode), ln=1)
    pdf.cell(0, 8, _safe_text(f"生成时间：{_fmt_dt(datetime.utcnow())}", use_unicode), ln=1)
    pdf.ln(2)

    # 申请人
    applicant = reservation.user
    pdf.set_font(font_name, "", 13)
    pdf.cell(0, 10, _safe_text("申请人信息", use_unicode), ln=1)
    if applicant:
        _kv(pdf, "姓名：", applicant.name, font_name, use_unicode)
        _kv(pdf, "身份：", _borrower_label(reservation), font_name, use_unicode)
        if applicant.college:
            _kv(pdf, "院系：", applicant.college, font_name, use_unicode)
        if applicant.student_no:
            _kv(pdf, "学号：", applicant.student_no, font_name, use_unicode)
        if applicant.teacher_no:
            _kv(pdf, "工号：", applicant.teacher_no, font_name, use_unicode)
        if applicant.org_name:
            _kv(pdf, "单位：", applicant.org_name, font_name, use_unicode)
        _kv(pdf, "联系方式：", reservation.contact or applicant.contact or "-", font_name, use_unicode)
    pdf.ln(2)

    # 设备
    device = reservation.device
    pdf.set_font(font_name, "", 13)
    pdf.cell(0, 10, _safe_text("设备信息", use_unicode), ln=1)
    if device:
        _kv(pdf, "设备编号：", device.device_no, font_name, use_unicode)
        _kv(pdf, "型号：", device.model, font_name, use_unicode)
        _kv(pdf, "用途：", device.usage, font_name, use_unicode)
    _kv(
        pdf,
        "预约时间：",
        f"{_fmt_dt(reservation.start_time)} - {_fmt_dt(reservation.end_time)}",
        font_name,
        use_unicode,
    )
    _kv(pdf, "预约描述：", reservation.description or "-", font_name, use_unicode)
    pdf.ln(2)

    # 审批
    pdf.set_font(font_name, "", 13)
    pdf.cell(0, 10, _safe_text("审批信息", use_unicode), ln=1)
    _kv(pdf, "当前状态：", _status_label(reservation.status), font_name, use_unicode)
    _kv(pdf, "当前节点：", _step_label(reservation.current_step), font_name, use_unicode)
    if reservation.advisor:
        _kv(
            pdf,
            "导师：",
            f"{reservation.advisor.name}（{_fmt_dt(reservation.advisor_approval_time)}）",
            font_name,
            use_unicode,
        )
        if reservation.advisor_comment:
            _kv(pdf, "导师意见：", reservation.advisor_comment, font_name, use_unicode)
    if reservation.approver:
        _kv(
            pdf,
            "设备管理员：",
            f"{reservation.approver.name}（{_fmt_dt(reservation.approval_time)}）",
            font_name,
            use_unicode,
        )
        if reservation.approval_comment:
            _kv(pdf, "管理员意见：", reservation.approval_comment, font_name, use_unicode)
    if reservation.head:
        _kv(
            pdf,
            "负责人：",
            f"{reservation.head.name}（{_fmt_dt(reservation.head_approval_time)}）",
            font_name,
            use_unicode,
        )
        if reservation.head_comment:
            _kv(pdf, "负责人意见：", reservation.head_comment, font_name, use_unicode)
    pdf.ln(2)

    # 财务
    pdf.set_font(font_name, "", 13)
    pdf.cell(0, 10, _safe_text("支付信息", use_unicode), ln=1)
    _kv(pdf, "金额：", f"{reservation.payment_amount:.2f}", font_name, use_unicode)
    _kv(pdf, "支付状态：", _payment_status_label(reservation.payment_status), font_name, use_unicode)
    if reservation.payment_order_no:
        _kv(pdf, "支付单号：", reservation.payment_order_no, font_name, use_unicode)
    if reservation.payment_time:
        _kv(pdf, "支付时间：", _fmt_dt(reservation.payment_time), font_name, use_unicode)
    if reservation.payment_voucher_ref:
        _kv(pdf, "凭证号：", reservation.payment_voucher_ref, font_name, use_unicode)
    if reservation.refund_amount:
        _kv(pdf, "退款金额：", f"{reservation.refund_amount:.2f}", font_name, use_unicode)
    if reservation.refund_time:
        _kv(pdf, "退款时间：", _fmt_dt(reservation.refund_time), font_name, use_unicode)
    pdf.ln(2)

    # 交接
    pdf.set_font(font_name, "", 13)
    pdf.cell(0, 10, _safe_text("借还交接", use_unicode), ln=1)
    _kv(pdf, "借出时间：", _fmt_dt(reservation.borrow_time), font_name, use_unicode)
    _kv(pdf, "归还时间：", _fmt_dt(reservation.return_time), font_name, use_unicode)
    if reservation.handover_note:
        _kv(pdf, "借出备注：", reservation.handover_note, font_name, use_unicode)
    if reservation.return_note:
        _kv(pdf, "归还备注：", reservation.return_note, font_name, use_unicode)
    pdf.ln(5)

    # 签章区域 - 根据申请人身份动态生成
    pdf.set_font(font_name, "", 13)
    pdf.cell(0, 10, _safe_text("签字盖章", use_unicode), ln=1)
    pdf.ln(3)
    
    pdf.set_font(font_name, "", 11)
    col_width = (pdf.w - pdf.l_margin - pdf.r_margin) / 2  # 两列布局
    
    # 获取申请人身份
    borrower_type = applicant.borrower_type if applicant else None
    
    if borrower_type == BorrowerType.TEACHER:
        # 教师：申请人签名 + 设备管理员签名
        pdf.cell(0, 8, _safe_text("申请人（教师）签名：_______________   日期：_______________", use_unicode), border=0, ln=1)
        pdf.ln(5)
        pdf.cell(0, 8, _safe_text("设备管理员签名：_______________   日期：_______________", use_unicode), border=0, ln=1)
        
    elif borrower_type == BorrowerType.STUDENT:
        # 学生：申请人签名 + 导师签名 + 设备管理员签名
        pdf.cell(0, 8, _safe_text("申请人（学生）签名：_______________   日期：_______________", use_unicode), border=0, ln=1)
        pdf.ln(5)
        pdf.cell(0, 8, _safe_text("指导教师签名：_______________   日期：_______________", use_unicode), border=0, ln=1)
        pdf.ln(5)
        pdf.cell(0, 8, _safe_text("设备管理员签名：_______________   日期：_______________", use_unicode), border=0, ln=1)
        
    elif borrower_type == BorrowerType.EXTERNAL:
        # 校外人员：申请人签名 + 设备管理员签名 + 负责人签名 + 财务章
        pdf.cell(0, 8, _safe_text("申请人（校外）签名：_______________   日期：_______________", use_unicode), border=0, ln=1)
        pdf.ln(5)
        pdf.cell(0, 8, _safe_text("设备管理员签名：_______________   日期：_______________", use_unicode), border=0, ln=1)
        pdf.ln(5)
        pdf.cell(0, 8, _safe_text("实验室负责人签名：_______________   日期：_______________", use_unicode), border=0, ln=1)
        pdf.ln(5)
        pdf.cell(0, 8, _safe_text("财务确认（盖章）：", use_unicode), border=0, ln=1)
        pdf.ln(12)  # 为财务章留出空间
        
    else:
        # 默认情况（未知身份）
        pdf.cell(0, 8, _safe_text("申请人签名：_______________   日期：_______________", use_unicode), border=0, ln=1)
        pdf.ln(3)
        pdf.cell(0, 8, _safe_text("审批人签名：_______________   日期：_______________", use_unicode), border=0, ln=1)
    
    pdf.ln(10)  # 底部留白

    # 输出
    # pdf.output(dest="S") 返回 bytearray，直接转换为 bytes
    out = bytes(pdf.output(dest="S"))
    return out
