from sqlalchemy import Column, Integer, String, Date, Text, Boolean
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    Model for Users in DB
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50))
    email = Column(String(100))
    phone = Column(String(20))
    birthdate = Column(Date)
    additional_data = Column(Text, nullable=True)
    account_id = Column("account_id", ForeignKey("accounts.id", ondelete="CASCADE"), default=None)
    login = relationship("Account", backref="users")


class Account(Base):
    """
    Model for Accounts in DB
    """
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    login = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
