from datetime import date as date_type, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import TaskPriority, TaskStatus


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=72)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=500)
    status: TaskStatus = TaskStatus.pendiente
    priority: TaskPriority = TaskPriority.medium
    date: Optional[date_type] = None
    due_date: Optional[date_type] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        clean_value = value.strip()
        if not clean_value:
            raise ValueError("Title cannot be empty")
        return clean_value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        clean_value = value.strip()
        return clean_value or None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=120)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    date: Optional[date_type] = None
    due_date: Optional[date_type] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        clean_value = value.strip()
        if not clean_value:
            raise ValueError("Title cannot be empty")
        return clean_value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        clean_value = value.strip()
        return clean_value or None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    date: date_type
    due_date: Optional[date_type] = None
    completed_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[TaskResponse]


class BulkTaskRequest(BaseModel):
    task_ids: List[int] = Field(..., min_length=1, max_length=100)


class BulkTaskResponse(BaseModel):
    processed_ids: List[int]
    not_found_ids: List[int]


class TaskStatsResponse(BaseModel):
    total: int
    pending: int
    completed: int
    created_today: int
    overdue: int
    due_soon: int
    deleted: int


class TaskAuditLogResponse(BaseModel):
    id: int
    task_id: int
    user_id: int
    action: str
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
