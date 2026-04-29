from datetime import date as date_type, timedelta
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.audit import add_changed_fields_audit, add_task_audit
from app.database import get_db
from app.models import TaskModel, TaskPriority, TaskStatus, UserModel, utc_now
from app.schemas import (
    BulkTaskRequest,
    BulkTaskResponse,
    TaskAuditLogResponse,
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskStatsResponse,
    TaskUpdate,
)
from app.security import get_current_user


router = APIRouter(prefix="/tasks", tags=["tasks"])

SORT_FIELDS = {
    "id": TaskModel.id,
    "date": TaskModel.date,
    "title": TaskModel.title,
    "status": TaskModel.status,
    "priority": TaskModel.priority,
    "due_date": TaskModel.due_date,
}


def get_owned_task(db: Session, task_id: int, user_id: int, include_deleted: bool = False) -> TaskModel:
    query = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.user_id == user_id)
    if not include_deleted:
        query = query.filter(TaskModel.deleted_at.is_(None))

    task = query.first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def normalize_task_data(task_data: dict):
    for field in ("status", "priority"):
        if field in task_data and task_data[field] is not None:
            task_data[field] = task_data[field].value
    return task_data


@router.get("/stats", response_model=TaskStatsResponse)
def get_task_stats(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    today = date_type.today()
    soon = today + timedelta(days=7)
    base_query = db.query(TaskModel).filter(TaskModel.user_id == current_user.id)
    active_query = base_query.filter(TaskModel.deleted_at.is_(None))

    return TaskStatsResponse(
        total=active_query.count(),
        pending=active_query.filter(TaskModel.status == TaskStatus.pendiente.value).count(),
        completed=active_query.filter(TaskModel.status == TaskStatus.completada.value).count(),
        created_today=active_query.filter(TaskModel.date == today).count(),
        overdue=active_query.filter(
            TaskModel.due_date.is_not(None),
            TaskModel.due_date < today,
            TaskModel.status != TaskStatus.completada.value,
        ).count(),
        due_soon=active_query.filter(
            TaskModel.due_date.is_not(None),
            TaskModel.due_date >= today,
            TaskModel.due_date <= soon,
            TaskModel.status != TaskStatus.completada.value,
        ).count(),
        deleted=base_query.filter(TaskModel.deleted_at.is_not(None)).count(),
    )


@router.post("/bulk/complete", response_model=BulkTaskResponse)
def complete_tasks_bulk(
    payload: BulkTaskRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    tasks = (
        db.query(TaskModel)
        .filter(TaskModel.user_id == current_user.id, TaskModel.id.in_(payload.task_ids), TaskModel.deleted_at.is_(None))
        .all()
    )
    found_ids = {task.id for task in tasks}
    now = utc_now()

    for task in tasks:
        task.status = TaskStatus.completada.value
        task.completed_at = now
        add_task_audit(db, task_id=task.id, user_id=current_user.id, action="bulk_completed")

    db.commit()
    return BulkTaskResponse(
        processed_ids=sorted(found_ids),
        not_found_ids=[task_id for task_id in payload.task_ids if task_id not in found_ids],
    )


@router.post("/bulk/delete", response_model=BulkTaskResponse)
def delete_tasks_bulk(
    payload: BulkTaskRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    tasks = (
        db.query(TaskModel)
        .filter(TaskModel.user_id == current_user.id, TaskModel.id.in_(payload.task_ids), TaskModel.deleted_at.is_(None))
        .all()
    )
    found_ids = {task.id for task in tasks}
    now = utc_now()

    for task in tasks:
        task.deleted_at = now
        add_task_audit(db, task_id=task.id, user_id=current_user.id, action="bulk_deleted")

    db.commit()
    return BulkTaskResponse(
        processed_ids=sorted(found_ids),
        not_found_ids=[task_id for task_id in payload.task_ids if task_id not in found_ids],
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    db_task = TaskModel(
        title=task.title,
        description=task.description,
        status=task.status.value,
        priority=task.priority.value,
        date=task.date or date_type.today(),
        due_date=task.due_date,
        user_id=current_user.id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    add_task_audit(db, task_id=db_task.id, user_id=current_user.id, action="created")
    db.commit()
    return db_task


@router.get("", response_model=TaskListResponse)
def list_tasks(
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    date: Optional[date_type] = None,
    priority: Optional[TaskPriority] = None,
    search: Optional[str] = Query(None, min_length=1, max_length=120),
    due: Optional[Literal["overdue", "soon"]] = None,
    include_deleted: bool = False,
    deleted_only: bool = False,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: Literal["id", "date", "title", "status", "priority", "due_date"] = "id",
    sort_order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    query = db.query(TaskModel).filter(TaskModel.user_id == current_user.id)

    if deleted_only:
        query = query.filter(TaskModel.deleted_at.is_not(None))
    elif not include_deleted:
        query = query.filter(TaskModel.deleted_at.is_(None))

    if status_filter:
        query = query.filter(TaskModel.status == status_filter.value)
    if date:
        query = query.filter(TaskModel.date == date)
    if priority:
        query = query.filter(TaskModel.priority == priority.value)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(or_(TaskModel.title.ilike(pattern), TaskModel.description.ilike(pattern)))

    today = date_type.today()
    if due == "overdue":
        query = query.filter(
            TaskModel.due_date.is_not(None),
            TaskModel.due_date < today,
            TaskModel.status != TaskStatus.completada.value,
        )
    elif due == "soon":
        query = query.filter(
            TaskModel.due_date.is_not(None),
            TaskModel.due_date >= today,
            TaskModel.due_date <= today + timedelta(days=7),
            TaskModel.status != TaskStatus.completada.value,
        )

    total = query.count()
    sort_column = SORT_FIELDS[sort_by]
    query = query.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
    tasks = query.offset(offset).limit(limit).all()

    return TaskListResponse(total=total, limit=limit, offset=offset, items=tasks)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task_details(task_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    return get_owned_task(db, task_id, current_user.id)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    task = get_owned_task(db, task_id, current_user.id)
    update_data = normalize_task_data(task_update.model_dump(exclude_unset=True))

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    old_values = {field: getattr(task, field) for field in update_data.keys()}

    for field, value in update_data.items():
        setattr(task, field, value)

    if update_data.get("status") == TaskStatus.completada.value and old_values.get("status") != TaskStatus.completada.value:
        task.completed_at = utc_now()
    elif update_data.get("status") == TaskStatus.pendiente.value:
        task.completed_at = None

    db.commit()
    db.refresh(task)
    add_changed_fields_audit(
        db,
        task_id=task.id,
        user_id=current_user.id,
        fields=update_data.keys(),
        old_values=old_values,
        new_values={field: getattr(task, field) for field in update_data.keys()},
    )
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    task = get_owned_task(db, task_id, current_user.id)
    old_status = task.status
    task.status = TaskStatus.completada.value
    task.completed_at = utc_now()
    db.commit()
    db.refresh(task)
    add_task_audit(
        db,
        task_id=task.id,
        user_id=current_user.id,
        action="completed",
        field_name="status",
        old_value=old_status,
        new_value=task.status,
    )
    db.commit()
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    task = get_owned_task(db, task_id, current_user.id)
    task.deleted_at = utc_now()
    add_task_audit(db, task_id=task.id, user_id=current_user.id, action="soft_deleted")
    db.commit()
    return None


@router.patch("/{task_id}/restore", response_model=TaskResponse)
def restore_task(task_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    task = get_owned_task(db, task_id, current_user.id, include_deleted=True)
    if task.deleted_at is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task is not deleted")

    task.deleted_at = None
    add_task_audit(db, task_id=task.id, user_id=current_user.id, action="restored")
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}/history", response_model=list[TaskAuditLogResponse])
def get_task_history(task_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    task = get_owned_task(db, task_id, current_user.id, include_deleted=True)
    return task.audit_logs
