from fastapi import FastAPI, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from models import Expense
from typing import Annotated
from starlette import status

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependecny = Annotated[Session,Depends(get_db)]

class ExpenseRequest(BaseModel):
    expense_name:str = Field(min_length=3, max_lenth=50)
    amount:float = Field(gt=0)
    date:str = Field(min_length=10)


@app.get("/expenses",status_code=status.HTTP_200_OK)
async def read_expenses(db: db_dependecny):
    return db.query(Expense).all()

@app.get('/expense/{expense_id}',status_code=status.HTTP_200_OK)
async def get_expense_by_id(db:db_dependecny,expense_id:int = Path(gt=0)):
    expense_model = db.query(Expense).filter(Expense.id == expense_id).first()
    if expense_model is not None:
        return expense_model
    raise HTTPException(status_code=404,detail="Expense not found.")

@app.post('/expenses/create_expense')
async def create_new_expense(db:db_dependecny,expenserequest:ExpenseRequest):
    expense_model = Expense(**expenserequest.model_dump())

    db.add(expense_model)
    db.commit()

@app.put('/expenses/{expense_id}')
async def update_expense_by_id(db:db_dependecny,expense_request:ExpenseRequest,expense_id:int = Path(gt=0)):
    expense_model = db.query(Expense).filter(Expense.id == expense_id).first()
    if expense_model is None:
        raise HTTPException(status_code=404,detail="Expense not found.")
    
    expense_model.amount = expense_request.amount
    expense_model.expense_name = expense_request.expense_name
    expense_model.date = expense_request.date

    db.add(expense_model)
    db.commit()

@app.delete('/expenses/{expense_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_by_id(db:db_dependecny,expense_id:int = Path(gt=0)):
    expense_model = db.query(Expense).filter(Expense.id == expense_id)
    if expense_model is None:
        raise HTTPException(status_code=404,detail="Expense not found.")
    
    db.query(Expense).filter(Expense.id == expense_id).delete()
    db.commit()