from test.utils import *

def test_read_all_expenses(dummy_expense):
    response = client.get('/expense/get_all')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'id':1,
        'expense_name':'New Expense',
        'amount':500.0,
        'date':'2024-03-22',
        'owner_expeense_id':1
    }]

def test_read_one_expense(dummy_expense):
    response = client.get('/expense/1')
    assert response.status_code == 200
    assert response.json() == {'expense_name':'New Expense','amount':500.0,'id':1,'owner_expeense_id':1,'date':'2024-03-22'}

def test_expense_not_found(dummy_expense):
    response = client.get('/expense/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_one_expense(dummy_expense):

    new_expense = {
        'expense_name':'One more expense',
        'amount':300.0,
        'date':'2024-10-11',
        'owner_expeense_id':1
    }

    response = client.post('/expense/create_expense', json = new_expense)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSession()
    model = db.query(Expense).filter(Expense.id == 2).first()
    assert model is not None
    assert model.expense_name == new_expense.get('expense_name')
    assert model.amount == new_expense.get('amount')
    assert str(model.date) == new_expense.get('date')
    assert model.owner_expeense_id == new_expense.get('owner_expeense_id')

def test_update_one_expense(dummy_expense):
    updated_expense = {
        'expense_name':'New Expense',
        'amount':300.0,
        'date':'2024-03-22',
        'owner_expeense_id':1
    }

    response = client.put('/expense/1', json = updated_expense)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSession()
    model = db.query(Expense).filter(Expense.id == 1).first()

    assert model.amount == updated_expense.get('amount')
    db.close()

def test_update_expense_not_found(dummy_expense):
    updated_expense = {
        'expense_name':'New Expense',
        'amount':300.0,
        'date':'2024-03-22',
        'owner_expeense_id':1
    }
    response = client.put('/expense/999', json=updated_expense)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':'Expense not found.'}

def test_delete_expense(dummy_expense):
    response = client.delete('/expense/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSession()
    model = db.query(Expense).filter(Expense.id == 1).first()

    assert model is None

def test_delete_expense_not_found(dummy_expense):
    response = client.delete('/expense/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':'Expense not found.'}
