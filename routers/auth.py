from fastapi import APIRouter, Depends, status, HTTPException
from database import get_db
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from pydantic import Field, BaseModel
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/auth", tags=["auth"])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db_dependency = Annotated[Session, Depends(get_db)]

SECRET_KEY = "047936d65ccdda44af4a9babb27257036326ef1ba8a6269b71328a67584ebc37"
ALGORITHM = "HS256"

oath2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token") # has to match @router.post("/token")

def create_access_token(username: str, user_id: int, user_role: str, expires_delta: timedelta):
    payload = { "sub": username, "id": user_id, "role": user_role }
    expires_time = datetime.now(timezone.utc) + expires_delta
    payload.update({ "exp": expires_time })
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def authenticate_user(username: str, password: str, db: db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user

async def get_current_user(token: Annotated[str, Depends(oath2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credential")
        return {"username": username, "id": user_id, "role": user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credential")


class CreateUserRequest(BaseModel):
    email: str = Field(max_length=50, min_length=5)
    username: str = Field(max_length=30, min_length=3)
    firstname: Optional[str] = Field(default=None, max_length=30)
    lastname: Optional[str] = Field(default=None, max_length=30)
    password: str = Field(min_length=5)
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    # new_user = Users(**create_user_request.model_dump()) will not work because password and hashed_password does not match
    new_user = Users(email=create_user_request.email,
                     username=create_user_request.username,
                     first_name=create_user_request.firstname,
                     last_name=create_user_request.lastname,
                     is_active=True,
                     role=create_user_request.role,
                     hashed_password=bcrypt_context.hash(create_user_request.password)
                     )
    db.add(new_user)
    db.commit()   
             
@router.post("/token", response_model=Token)
async def login_to_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credential")
    token = create_access_token(username=user.username, user_id=user.id, user_role=user.role, expires_delta=timedelta(minutes=20))
    return Token(access_token=token, token_type="bearer")