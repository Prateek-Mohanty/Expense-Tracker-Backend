from pydantic import BaseModel
from datetime import date

class ExpenseCreate(BaseModel):
    expense_name:str
    amount:float
    date:date

class Expense(BaseModel):
    id:int
    expense_name:str
    amount:float
    date:date

    class Config:
        orm_mode = True