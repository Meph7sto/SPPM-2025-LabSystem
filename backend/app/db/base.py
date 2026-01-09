from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from ..models import user, device, reservation  # noqa: E402,F401
