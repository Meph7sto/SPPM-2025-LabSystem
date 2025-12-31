from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from ..models import user  # noqa: E402,F401
