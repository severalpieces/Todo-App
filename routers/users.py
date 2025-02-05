from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import Field, BaseModel
import models
from database import get_db
from sqlalchemy.orm import Session
from .auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(prefix="/user", tags=["user"])

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    user_info = db.query(models.Users).filter_by(id=user.get("id")).first()
    # if user_info is None:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user_info

class PutRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=5)

class PhoneNumberChangeRequest(BaseModel):
    password: str
    new_phone_number: str = Field(max_length=30)

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, put_request: PutRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    current_user_info = db.query(models.Users).filter_by(id=user.get("id")).first()
    # if current_user_info is None:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not bcrypt_context.verify(put_request.current_password, current_user_info.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is wrong")
    current_user_info.hashed_password = bcrypt_context.hash(put_request.new_password)
    db.commit()

@router.put("/phone_number", status_code=status.HTTP_200_OK)
async def change_phone_number(user: user_dependency, db: db_dependency, phone_number_request: PhoneNumberChangeRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    db_user = db.query(models.Users).filter_by(id=user.get("id")).first()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not bcrypt_context.verify(phone_number_request.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="password is wrong")
    db_user.phone_number = phone_number_request.new_phone_number
    db.commit()
    db.refresh(db_user)
    return db_user