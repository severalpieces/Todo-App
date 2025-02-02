from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Path, HTTPException
from pydantic import Field, field_validator, BaseModel
import models
from database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(models.Todos).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(models.Todos).filter(
        models.Todos.id == todo_id).first()  # save some time by adding .first()
    if todo_model is not None:
        return todo_model
    else:
        raise HTTPException(status_code=404, detail="todo not found")


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=30)
    description: Optional[str] = Field(default=None, max_length=100)
    priority: Optional[int] = Field(default=None, gt=0, le=5)
    complete: bool = Field(default=False)

    @field_validator("description")
    def validate_description(cls, value):
        if value and value == "you are a fool":
            raise ValueError("Don't insult me")
        return value


@router.post("/todo", status_code=status.HTTP_200_OK)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    new_todo = models.Todos(**todo_request.model_dump())
    db.add(new_todo)
    db.commit()

    added_todo = db.query(models.Todos).filter_by(
        title=new_todo.title, description=new_todo.description, priority=new_todo.priority, complete=new_todo.complete).first()
    if added_todo:
        return added_todo
    else:
        raise HTTPException(status_code=500, detail="Failed to add a new todo")


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    todo = db.query(models.Todos).filter_by(id=todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")

    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.complete = todo_request.complete
    todo.priority = todo_request.priority

    db.commit()


class PatchRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=30)
    description: Optional[str] = Field(default=None, max_length=100)
    priority: Optional[int] = Field(default=None, gt=0, le=5)
    complete: Optional[bool] = Field(default=None)

    @field_validator("description")
    def validate_description(cls, value):
        if value and value == "you are a fool":
            raise ValueError("Don't insult me")
        return value


@router.patch("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def patch_todo(db: db_dependency, todo_request: PatchRequest, todo_id: int = Path(gt=0)):
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")

    todo.title = todo.title if todo_request.title is None else todo_request.title
    todo.description = todo.description if todo_request.description is None else todo_request.description
    todo.priority = todo.priority if todo_request.priority is None else todo_request.priority
    todo.complete = todo.complete if todo_request.complete is None else todo_request.complete

    db.commit()
    return todo


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    db.delete(todo)
    db.commit()
