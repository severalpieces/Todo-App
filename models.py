from sqlalchemy import ForeignKey, String
from database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import field_validator
from typing import List, Optional


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(30), default=None)
    last_name: Mapped[Optional[str]] = mapped_column(String(30), default=None)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str]

    todos: Mapped[List["Todos"]] = relationship(
        back_populates="user", cascade="all, delete-orphan")

    # Base creates __init__ automatically

    @field_validator("email")
    def validate_email(cls, value: str) -> str:
        if len(value) < 5:
            raise ValueError("email cannot be less than 5 characters")
        return value

    @field_validator("username")
    def validate_username(cls, value: str) -> str:
        if len(value) < 3:
            raise ValueError("username cannot be shorter than 3 characters")
        return value


class Todos(Base):
    __tablename__ = "todos"

    # index = True makes the id unique
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]]
    priority: Mapped[Optional[int]]
    complete: Mapped[bool] = mapped_column(default=False)
    owner: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["Users"] = relationship(back_populates="todos")
