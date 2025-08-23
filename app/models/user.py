from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from . import Base

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    display_name = Column(Text, nullable=False)
    email = Column(Text, unique=True)
    password_hash = Column(Text)
    auth_provider = Column(Text)
    auth_sub = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "(email IS NOT NULL OR (auth_provider IS NOT NULL AND auth_sub IS NOT NULL))",
            name="users_email_or_social"
        ),
        CheckConstraint(
            "auth_provider IN ('kakao', 'google')",
            name="users_auth_provider_check"
        ),
        UniqueConstraint("auth_provider", "auth_sub"),
    )
