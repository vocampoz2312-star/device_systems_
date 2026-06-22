from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    device_id: Mapped[int] = mapped_column(Integer, ForeignKey("devices.id"), nullable=False)
    loan_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    return_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    user = relationship("User", back_populates="loans")
    device = relationship("Device", back_populates="loans")

    def __repr__(self) -> str:
        return f"<Loan id={self.id} user={self.user_id} device={self.device_id} status={self.status!r}>"
