from sqlalchemy import Integer, Column, String, Float, Date, ForeignKey, Boolean
from database import Base

class Expense(Base):
    __tablename__ = 'Expenses'

    id = Column(Integer, primary_key=True, index=True)
    expense_name = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    owner_expeense_id = Column(Integer, ForeignKey('Users.id'))


class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer,primary_key=True, index = True)
    user_name = Column(String(40),unique=True) 
    email = Column(String(40), unique=True)
    first_name = Column(String(40))
    last_name = Column(String(40))
    is_active = Column(Boolean, default=True)
    role = Column(String(20))
    hashed_password = Column(String)
