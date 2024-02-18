from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50))
    email = Column(String(100))
    phone = Column(String(20))
    birthdate = Column(Date)
    additional_data = Column(Text, nullable=True)
