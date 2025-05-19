from sqlalchemy import Integer, Column, String, Float, Date
from database import Base

class Expense(Base):
    __tablename__ = 'Expenses'

    id = Column(Integer, primary_key=True, index=True)
    expense_name = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)