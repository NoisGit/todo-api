from datetime import date as date_type
from enum import Enum
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker, Session


DATABASE_URL = "sqlite:///./tasks.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class TaskStatus(str, Enum):
    pendiente = "pendiente"
    completada = "completada"


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default=TaskStatus.pendiente.value)
    date = Column(Date, nullable=False, default=date_type.today)


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.pendiente
    date: Optional[date_type] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    date: Optional[date_type] = None


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    date: date_type

    model_config = ConfigDict(from_attributes=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="To-Do API con SQLite")

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "API de tareas funcionando"}


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskModel(
        title=task.title,
        description=task.description,
        status=task.status.value,
        date=task.date or date_type.today(),
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks", response_model=List[Task])
def list_tasks(db: Session = Depends(get_db)):
    tasks = db.query(TaskModel).all()
    return tasks


@app.get("/tasks/{details_id}", response_model=Task)
def get_task_details(details_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == details_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@app.put("/tasks/{update_id}", response_model=Task)
def update_task(update_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == update_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    update_data = task_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    for field, value in update_data.items():
        if field == "status" and value is not None:
            value = value.value
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{delete_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(delete_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == delete_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    db.delete(task)
    db.commit()
    return None
