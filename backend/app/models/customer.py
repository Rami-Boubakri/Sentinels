from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    segment = Column(String)
    loan_size = Column(Float)
    risk_stage = Column(Integer)
