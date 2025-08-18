from fastapi import Depends, HTTPException, Path, APIRouter
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Expense
from typing import Annotated
from starlette import status
from datetime import date
from .auth import get_current_user

router = APIRouter(
    prefix = '/expense',
    tags=['Expenses']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependecny = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict,Depends(get_current_user)]

class ExpenseRequest(BaseModel):
    expense_name:str = Field(min_length=3, max_length=50)
    amount:float = Field(gt=0)
    date:date


@router.get("/get_all",status_code=status.HTTP_200_OK)
async def read_expenses(user:user_dependency, db: db_dependecny):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized access blocked')
    return db.query(Expense).filter(Expense.owner_expeense_id == user.get('id')).all()

@router.get('/{expense_id}',status_code=status.HTTP_200_OK)
async def get_expense_by_id(user:user_dependency, db:db_dependecny, expense_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized access blocked')    
    expense_model = db.query(Expense).filter(Expense.id == expense_id).filter(Expense.owner_expeense_id == user.get('id')).first()
    if expense_model is not None:
        return expense_model
    raise HTTPException(status_code=404,detail="Expense not found.")

@router.post('/create_expense', status_code = status.HTTP_201_CREATED)
async def create_new_expense(user:user_dependency, db:db_dependecny, expenserequest:ExpenseRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized access blocked')
    expense_model = Expense(**expenserequest.model_dump(), owner_expeense_id = user.get('id'))
    db.add(expense_model)
    db.commit()

@router.put('/{expense_id}', status_code = status.HTTP_204_NO_CONTENT)
async def update_expense_by_id(user:user_dependency, db:db_dependecny,expense_request:ExpenseRequest,expense_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized access blocked')
    expense_model = db.query(Expense).filter(Expense.id == expense_id).filter(Expense.owner_expeense_id == user.get('id')).first()
    if expense_model is None:
        raise HTTPException(status_code=404,detail="Expense not found.")
    
    expense_model.amount = expense_request.amount
    expense_model.expense_name = expense_request.expense_name
    expense_model.date = expense_request.date

    db.add(expense_model)
    db.commit()

@router.delete('/{expense_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_by_id(user:user_dependency, db:db_dependecny,expense_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Unauthorized access blocked')
    expense_model = db.query(Expense).filter(Expense.id == expense_id).filter(Expense.owner_expeense_id == user.get('id')).first()
    if expense_model is None:
        raise HTTPException(status_code=404,detail="Expense not found.")
    db.query(Expense).filter(Expense.id == expense_id).filter(Expense.owner_expeense_id == user.get('id')).delete()
    db.commit()