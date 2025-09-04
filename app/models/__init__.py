from sqlalchemy.orm import declarative_base

Base = declarative_base()

# 모든 모델들을 import
from .place import Place
from .menu import Menu
from .review import Review

__all__ = ["Base", "Place", "Menu", "Review"]
