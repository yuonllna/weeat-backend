from sqlalchemy import Column, BigInteger, Text, Integer, ForeignKey, CheckConstraint, Index
from . import Base

class Menu(Base):
    __tablename__ = "menus"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    place_id = Column(BigInteger, ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    price = Column(Integer)

    __table_args__ = (
        CheckConstraint("price >= 0", name="menus_price_check"),
        Index("menus_place_idx", "place_id"),
    )
