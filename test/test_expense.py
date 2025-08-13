from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from database import Base
from routers import auth, expenses
import pytest
from models import Expense
from fastapi import status
from datetime import date

DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(DATABASE_URL,connect_args={'check_same_thread':False})

TestingSession = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username':'codingwithmetest','id':1}

app.dependency_overrides[auth.get_db] = override_get_db
app.dependency_overrides[expenses.get_db] = override_get_db
app.dependency_overrides[auth.get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture
def dummy_user():

    with engine.connect() as connection:
        connection.execute(text('DELETE FROM Expenses;'))
        connection.commit()

    expense = Expense(
        expense_name = 'New Expense', 
        amount = 500, 
        date = date(2024,3,22), 
        owner_expeense_id = 1
    )

    db = TestingSession()
    db.add(expense)
    db.commit()
    yield db


def test_read_all_expenses(dummy_user):
    response = client.get('/expense/get_all')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'id':1,
        'expense_name':'New Expense',
        'amount':500.0,
        'date':'2024-03-22',
        'owner_expeense_id':1
    }]

def test_read_one_expense(dummy_user):
    expense_id = dummy_user.query(Expense).first().id
    response = client.get(f'/expense/{expense_id}')
    assert response.status_code == 200
