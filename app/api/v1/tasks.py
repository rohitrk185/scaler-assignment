"""Tasks API Endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from app.database import get_db
from app.models.task import Task
from app.schemas.task import TaskResponse, TaskCreate, TaskUpdate
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.config import settings

router = APIRouter()


@router.get("/tasks", response_model=dict)
async def get_tasks(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all tasks.
    
    Returns a list of all tasks accessible to the authenticated user.
    """
    try:
        items = db.query(Task).all()
        
        paginated = create_paginated_response(
            items=items,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/tasks"
        )
        
        response_data = {
            "data": [
                TaskResponse(
                    gid=obj.gid,
                    resource_type=obj.resource_type,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                    name=obj.name,
                    resource_subtype=obj.resource_subtype,
                    created_by=obj.created_by,
                    approval_status=obj.approval_status,
                    assignee_status=obj.assignee_status,
                    completed=obj.completed,
                    completed_at=obj.completed_at,
                    due_at=obj.due_at,
                    due_on=obj.due_on,
                    external=obj.external,
                    html_notes=obj.html_notes,
                    hearted=obj.hearted,
                    is_rendered_as_separator=obj.is_rendered_as_separator,
                    liked=obj.liked,
                    memberships=obj.memberships,
                    modified_at=obj.modified_at,
                    notes=obj.notes,
                    num_hearts=obj.num_hearts,
                    num_likes=obj.num_likes,
                    num_subtasks=obj.num_subtasks,
                    start_at=obj.start_at,
                    start_on=obj.start_on,
                    actual_time_minutes=obj.actual_time_minutes,
                    permalink_url=obj.permalink_url,
                    dependencies=None,
                    dependents=None,
                    hearts=None,
                    likes=None,
                    custom_fields=None,
                    followers=None,
                    projects=None,
                    tags=None,
                    completed_by=None,
                    assignee=None,
                    assignee_section=None,
                    parent=None,
                    custom_type=None,
                    custom_type_status_option=None,
                    workspace=None
                ).model_dump(exclude_none=True)
                for obj in paginated.data
            ]
        }
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {
                "offset": paginated.next_offset,
                "path": f"{settings.API_V1_PREFIX}/tasks",
                "uri": f"{settings.API_V1_PREFIX}/tasks?limit={pagination.limit}&offset={paginated.next_offset}"
            }
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/tasks/{task_gid}", response_model=dict)
async def get_task(
    task_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific task.
    
    Returns the full record for a single task.
    """
    try:
        obj = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not obj:
            raise NotFoundError("Task", task_gid)
        
        obj_response = TaskResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            resource_subtype=obj.resource_subtype,
            created_by=obj.created_by,
            approval_status=obj.approval_status,
            assignee_status=obj.assignee_status,
            completed=obj.completed,
            completed_at=obj.completed_at,
            due_at=obj.due_at,
            due_on=obj.due_on,
            external=obj.external,
            html_notes=obj.html_notes,
            hearted=obj.hearted,
            is_rendered_as_separator=obj.is_rendered_as_separator,
            liked=obj.liked,
            memberships=obj.memberships,
            modified_at=obj.modified_at,
            notes=obj.notes,
            num_hearts=obj.num_hearts,
            num_likes=obj.num_likes,
            num_subtasks=obj.num_subtasks,
            start_at=obj.start_at,
            start_on=obj.start_on,
            actual_time_minutes=obj.actual_time_minutes,
            permalink_url=obj.permalink_url,
            dependencies=None,
            dependents=None,
            hearts=None,
            likes=None,
            custom_fields=None,
            followers=None,
            projects=None,
            tags=None,
            completed_by=None,
            assignee=None,
            assignee_section=None,
            parent=None,
            custom_type=None,
            custom_type_status_option=None,
            workspace=None
        )
        
        return format_success_response(obj_response)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.post("/tasks", response_model=dict)
async def create_task(
    task_data: TaskCreate,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a task.
    
    Creates a new task.
    """
    try:
        new_obj = Task(
            gid=str(uuid.uuid4()),
            resource_type="task",
            **task_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        obj_response = TaskResponse(
            gid=new_obj.gid,
            resource_type=new_obj.resource_type,
            created_at=new_obj.created_at,
            updated_at=new_obj.updated_at,
            name=new_obj.name,
            resource_subtype=new_obj.resource_subtype,
            created_by=new_obj.created_by,
            approval_status=new_obj.approval_status,
            assignee_status=new_obj.assignee_status,
            completed=new_obj.completed,
            completed_at=new_obj.completed_at,
            due_at=new_obj.due_at,
            due_on=new_obj.due_on,
            external=new_obj.external,
            html_notes=new_obj.html_notes,
            hearted=new_obj.hearted,
            is_rendered_as_separator=new_obj.is_rendered_as_separator,
            liked=new_obj.liked,
            memberships=new_obj.memberships,
            modified_at=new_obj.modified_at,
            notes=new_obj.notes,
            num_hearts=new_obj.num_hearts,
            num_likes=new_obj.num_likes,
            num_subtasks=new_obj.num_subtasks,
            start_at=new_obj.start_at,
            start_on=new_obj.start_on,
            actual_time_minutes=new_obj.actual_time_minutes,
            permalink_url=new_obj.permalink_url,
            dependencies=None,
            dependents=None,
            hearts=None,
            likes=None,
            custom_fields=None,
            followers=None,
            projects=None,
            tags=None,
            completed_by=None,
            assignee=None,
            assignee_section=None,
            parent=None,
            custom_type=None,
            custom_type_status_option=None,
            workspace=None
        )
        
        return format_success_response(obj_response, status_code=201)
    
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.put("/tasks/{task_gid}", response_model=dict)
async def update_task(
    task_gid: str,
    task_data: TaskUpdate,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a task.
    
    Updates the fields of a task. Only the fields provided in the request will be updated.
    """
    try:
        obj = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not obj:
            raise NotFoundError("Task", task_gid)
        
        update_dict = task_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        
        obj_response = TaskResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            resource_subtype=obj.resource_subtype,
            created_by=obj.created_by,
            approval_status=obj.approval_status,
            assignee_status=obj.assignee_status,
            completed=obj.completed,
            completed_at=obj.completed_at,
            due_at=obj.due_at,
            due_on=obj.due_on,
            external=obj.external,
            html_notes=obj.html_notes,
            hearted=obj.hearted,
            is_rendered_as_separator=obj.is_rendered_as_separator,
            liked=obj.liked,
            memberships=obj.memberships,
            modified_at=obj.modified_at,
            notes=obj.notes,
            num_hearts=obj.num_hearts,
            num_likes=obj.num_likes,
            num_subtasks=obj.num_subtasks,
            start_at=obj.start_at,
            start_on=obj.start_on,
            actual_time_minutes=obj.actual_time_minutes,
            permalink_url=obj.permalink_url,
            dependencies=None,
            dependents=None,
            hearts=None,
            likes=None,
            custom_fields=None,
            followers=None,
            projects=None,
            tags=None,
            completed_by=None,
            assignee=None,
            assignee_section=None,
            parent=None,
            custom_type=None,
            custom_type_status_option=None,
            workspace=None
        )
        
        return format_success_response(obj_response)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.delete("/tasks/{task_gid}", response_model=dict)
async def delete_task(
    task_gid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a task.
    
    Deletes a task.
    """
    try:
        obj = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not obj:
            raise NotFoundError("Task", task_gid)
        
        db.delete(obj)
        db.commit()
        
        return format_success_response({"data": {}}, status_code=200)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )
