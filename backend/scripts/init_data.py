import sys
import os
from datetime import date

# Ensure the backend directory is in the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(backend_dir)

from backend.app.db.session import SessionLocal
from backend.app.models.user import User, UserRole, BorrowerType
from backend.app.models.device import Device, DeviceStatus
from backend.app.core.security import hash_password

def init_db_data():
    db = SessionLocal()
    try:
        print("开始初始化演示数据...")

        # 1. 创建管理员 (Admin)
        admin = db.query(User).filter(User.account == "admin").first()
        if not admin:
            admin = User(
                account="admin",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN,
                name="系统管理员",
                contact="admin@lesms.com",
                is_active=True
            )
            db.add(admin)
            print(">> 创建管理员账号: admin / admin123")
        
        # 2. 创建负责人 (Head)
        head = db.query(User).filter(User.account == "head").first()
        if not head:
            head = User(
                account="head",
                password_hash=hash_password("head123"),
                role=UserRole.HEAD,
                name="实验室负责人",
                contact="head@lesms.com",
                is_active=True
            )
            db.add(head)
            print(">> 创建负责人账号: head / head123")

        # 3. 创建测试教师 (Teacher - 用于当导师)
        teacher = db.query(User).filter(User.account == "T1001").first()
        if not teacher:
            teacher = User(
                account="T1001",
                password_hash=hash_password("123456"),
                role=UserRole.BORROWER,
                borrower_type=BorrowerType.TEACHER,
                name="王教授",
                contact="13800001001",
                college="计算机学院",
                teacher_no="1001",
                is_active=True
            )
            db.add(teacher)
            print(">> 创建教师账号: T1001 / 123456")

        # 4. 创建一些设备
        devices = [
            {
                "device_no": "A001", "model": "MacBook Pro M3", 
                "manufacturer": "Apple", "usage": "高性能计算", 
                "rental_price": 50.0, "status": DeviceStatus.IDLE
            },
            {
                "device_no": "B001", "model": "Oscilloscope X100", 
                "manufacturer": "Tektronix", "usage": "电路测试", 
                "rental_price": 0.0, "status": DeviceStatus.IDLE
            },
            {
                "device_no": "C001", "model": "3D Printer Pro", 
                "manufacturer": "Creality", "usage": "模型打印", 
                "rental_price": 20.0, "status": DeviceStatus.MAINTENANCE
            },
        ]

        for d_data in devices:
            exists = db.query(Device).filter(Device.device_no == d_data["device_no"]).first()
            if not exists:
                device = Device(
                    device_no=d_data["device_no"],
                    model=d_data["model"],
                    purchase_date=date(2025, 1, 1),
                    manufacturer=d_data["manufacturer"],
                    usage=d_data["usage"],
                    rental_price=d_data["rental_price"],
                    status=d_data["status"]
                )
                db.add(device)
                print(f">> 创建设备: {d_data['device_no']} - {d_data['model']}")

        db.commit()
        print("数据初始化完成！")

    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db_data()
