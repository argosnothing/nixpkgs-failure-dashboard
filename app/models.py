from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Build(Base):
    __tablename__ = "builds"

    id = Column(Integer, primary_key=True)
    attrpath = Column(String, unique=True)
    status = Column(Enum("success", "failed", "timeout"))
