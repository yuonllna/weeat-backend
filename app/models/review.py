from sqlalchemy import Column, BigInteger, Text, Integer, String, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.sql import func
from . import Base

class Review(Base):
    __tablename__ = "reviews"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    place_id = Column(BigInteger, ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    rating = Column(Integer, nullable=False)
    content = Column(Text)
    photo_urls = Column(Text)  # JSON 배열 형태로 여러 장 저장
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="reviews_rating_check"),
    )
