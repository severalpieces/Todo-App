from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# engine = create_engine("sqlite:///todosapp.db", echo=True, connect_args={'check_same_thread': False})

engine = create_engine("mysql+pymysql://root:test1234!@127.0.0.1:3306/TodoApplicationDatabase")

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()