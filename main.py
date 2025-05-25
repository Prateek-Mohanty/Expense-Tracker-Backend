from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/expenses", response_model=list[schemas.Expense])
def read_expenses(db: Session = Depends(get_db)):
    try:
        return db.query(models.Expense).all()
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Failed to fetch from database: {str(e)}")

@app.post("/create_expense")
def create_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    try:
        db_expense = models.Expense(**expense.model_dump())
        db.add(db_expense)
        db.commit()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create expense: {str(e)}")