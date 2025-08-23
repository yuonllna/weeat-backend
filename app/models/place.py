from sqlalchemy import Column, BigInteger, Text, CheckConstraint, Index
from . import Base

class Place(Base):
    __tablename__ = "places"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    distance_note = Column(Text)
    address = Column(Text)
    hero_image_url = Column(Text)

    __table_args__ = (
        CheckConstraint(
            "category IN ('양식','일식','중식','한식','동남아','카페','지중해식','패스트푸드','그외')",
            name="places_category_check"
        ),
        Index("places_category_idx", "category"),
    )
