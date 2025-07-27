from fastapi import APIRouter, Depends, HTTPException
from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel
from models import Users
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from database import SessionLocal

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)

SECRET_KEY = '286cf13ee6113079c8ed37dcfef63dc843605d3b48c46cf94bc99639264d657f'
ALGORITHM = 'HS256'

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/token')

class User(BaseModel):
    email:str
    username:str
    firstname:str
    lastname:str
    password:str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
db_dependecny = Annotated[Session,Depends(get_db)]

def generate_token(username, user_id, expires:timedelta):
    encode = {'sub':username, 'id':user_id}
    expires = datetime.now(timezone.utc) + expires
    encode.update({'exp':expires})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

def authenticate_user(username,password,db):
    user = db.query(Users).filter(Users.user_name == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_name = payload.get('sub')
        user_id = payload.get('id')
        if user_name is None or user_id is None:
            raise HTTPException(status_code=401, detail='User not authorized')
        return {'username':user_name, 'id':user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail='Unauthorized user')

@router.post('/create_user',status_code=status.HTTP_200_OK)
async def create_new_user(user:User,db:db_dependecny):
    user_model = Users(
        user_name = user.username,
        email = user.email,
        first_name = user.firstname,
        last_name = user.lastname,
        hashed_password = bcrypt_context.hash(user.password),
        is_active = True
    )
    db.add(user_model)
    db.commit()

@router.get('/read_all_users')
async def read_all_users(db:db_dependecny):
    return db.query(Users).all()

@router.post('/token',status_code=status.HTTP_202_ACCEPTED)
async def get_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],db:db_dependecny):
    user = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized user')
    token = generate_token(user.user_name, user.id, timedelta(minutes=20))
    print(f'token: {token}')
    return {'access_token':token, 'token_type':'bearer'}
    