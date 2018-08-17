from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Account(Base):
    __tablename__ = 'accounts'

    acct = Column(String(140), primary_key=True)
