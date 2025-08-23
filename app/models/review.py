from sqlalchemy import Column, BigInteger, Text, Integer, Date, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.sql import func
from . import Base

class Review(Base):
    __tablename__ = "reviews"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    place_id = Column(BigInteger, ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    visited_at = Column(Date)
    menu = Column(Text)
    price_text = Column(Text)
    rating = Column(Integer, nullable=False)
    content = Column(Text)
    photo_url = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="reviews_rating_check"),
    )
