import enum
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.database import Base


class MemberRole(str, enum.Enum):
    LIBRARIAN = "Librarian"
    MEMBER = "Member"


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        SqlEnum(MemberRole, name="member_role_enum", values_callable=lambda obj: [e.value for e in obj]),
        default=MemberRole.MEMBER,
        nullable=False,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    registration_date = Column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )

    # Relationships
    loans = relationship("Loan", back_populates="member", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Member(id={self.id}, name='{self.name}', email='{self.email}', role='{self.role.value}')>"
