from typing import Any, Iterable

from sqlalchemy.orm import Session

from app.models import TaskAuditLogModel


def stringify(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def add_task_audit(
    db: Session,
    *,
    task_id: int,
    user_id: int,
    action: str,
    field_name: str | None = None,
    old_value: Any = None,
    new_value: Any = None,
) -> None:
    db.add(
        TaskAuditLogModel(
            task_id=task_id,
            user_id=user_id,
            action=action,
            field_name=field_name,
            old_value=stringify(old_value),
            new_value=stringify(new_value),
        )
    )


def add_changed_fields_audit(
    db: Session,
    *,
    task_id: int,
    user_id: int,
    fields: Iterable[str],
    old_values: dict[str, Any],
    new_values: dict[str, Any],
) -> None:
    for field in fields:
        old_value = old_values.get(field)
        new_value = new_values.get(field)
        if stringify(old_value) == stringify(new_value):
            continue
        add_task_audit(
            db,
            task_id=task_id,
            user_id=user_id,
            action="updated",
            field_name=field,
            old_value=old_value,
            new_value=new_value,
        )
