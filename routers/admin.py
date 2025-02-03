from typing import Annotated
from fastapi import APIRouter, Depends, status, Path, HTTPException
import models
from database import get_db
from sqlalchemy.orm import Session
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return db.query(models.Todos).all()

@router.delete("/delete/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    db.delete(todo)
    db.commit()