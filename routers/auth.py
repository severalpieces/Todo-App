from fastapi import APIRouter, Depends, status
from database import SessionLocal
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import Field, BaseModel
from models import Users
from passlib.context import CryptContext

router = APIRouter()

bycrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    email: str = Field(max_length=50, min_length=5)
    username: str = Field(max_length=30, min_length=3)
    firstname: Optional[str] = Field(default=None, max_length=30)
    lastname: Optional[str] = Field(default=None, max_length=30)
    password: str = Field(min_length=5)
    role: str


@router.post("/auth", status_code=status.HTTP_200_OK)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    # new_user = Users(**create_user_request.model_dump()) will not work because password and hashed_password does not match
    new_user = Users(email=create_user_request.email,
                     username=create_user_request.username,
                     first_name=create_user_request.firstname,
                     last_name=create_user_request.lastname,
                     is_active=True,
                     role=create_user_request.role,
                     hashed_password=bycrypt_context.hash(create_user_request.password))
    return new_user
