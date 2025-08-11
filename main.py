from fastapi import FastAPI
from database import engine
import models
from routers import expenses, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(expenses.router)
app.include_router(auth.router)


#testing rebase