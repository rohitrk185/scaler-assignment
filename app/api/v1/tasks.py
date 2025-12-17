"""Tasks API Endpoints"""
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
from app.database import get_db
from app.models.task import Task
from app.schemas.task import TaskResponse, TaskCreate, TaskUpdate
from app.schemas.common import (
    TaskDuplicateRequest, TaskAddProjectRequest, TaskRemoveProjectRequest,
    TaskAddTagRequest, TaskRemoveTagRequest, AddFollowersRequest, RemoveFollowersRequest,
    TaskSetParentRequest, ModifyDependenciesRequest, ModifyDependentsRequest, EmptyResponse
)
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
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
        # Validate GID format first (matches Asana behavior - returns 400 for invalid format)
        from app.utils.gid_validation import validate_gid_format
        validate_gid_format(task_gid, "task")
        
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
    
    except HTTPException:
        raise
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
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a task.
    
    Creates a new task.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        # Parse request body following OpenAPI spec format: {"data": {...}}
        task_data = parse_request_body(request_body, TaskCreate)
        
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
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a task.
    
    Updates the fields of a task. Only the fields provided in the request will be updated.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        # Validate GID format first (matches Asana behavior - returns 400 for invalid format)
        from app.utils.gid_validation import validate_gid_format
        validate_gid_format(task_gid, "task")
        
        obj = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not obj:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        task_data = parse_request_body(request_body, TaskUpdate)
        
        # Note: Asana allows empty names for projects/tasks (only rejects for users)
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
    
    except HTTPException:
        raise
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


def _build_task_response(task: Task) -> TaskResponse:
    """Helper function to build TaskResponse from Task model"""
    return TaskResponse(
        gid=task.gid,
        resource_type=task.resource_type,
        created_at=task.created_at,
        updated_at=task.updated_at,
        name=task.name,
        resource_subtype=task.resource_subtype,
        created_by=task.created_by,
        approval_status=task.approval_status,
        assignee_status=task.assignee_status,
        completed=task.completed,
        completed_at=task.completed_at,
        due_at=task.due_at,
        due_on=task.due_on,
        external=task.external,
        html_notes=task.html_notes,
        hearted=task.hearted,
        is_rendered_as_separator=task.is_rendered_as_separator,
        liked=task.liked,
        memberships=task.memberships,
        modified_at=task.modified_at,
        notes=task.notes,
        num_hearts=task.num_hearts,
        num_likes=task.num_likes,
        num_subtasks=task.num_subtasks,
        start_at=task.start_at,
        start_on=task.start_on,
        actual_time_minutes=task.actual_time_minutes,
        permalink_url=task.permalink_url,
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


@router.post("/tasks/{task_gid}/duplicate", response_model=dict)
async def duplicate_task(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Duplicate a task.
    
    Creates and returns a job that will asynchronously handle the duplication.
    Request body must follow OpenAPI spec format: {"data": {"name": "...", "include": "..."}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        duplicate_data = parse_request_body(request_body, TaskDuplicateRequest)
        
        # TODO: Implement actual duplication logic with async job
        # For now, return a simple job response
        import hashlib
        import time
        job_gid = hashlib.md5(f"{task_gid}_{duplicate_data.name or task.name}_{time.time()}".encode()).hexdigest()
        
        job_response = {
            "gid": job_gid,
            "resource_type": "job",
            "resource_subtype": "task_duplicate",
            "status": "pending"
        }
        
        return format_success_response(job_response, status_code=201)
    
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


@router.post("/tasks/{task_gid}/addProject", response_model=dict)
async def add_task_to_project(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Add a task to a project.
    
    Adds the task to the specified project.
    Returns the updated task record.
    Request body must follow OpenAPI spec format: {"data": {"project": "...", "insert_after": "...", "insert_before": "..."}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        add_project_data = parse_request_body(request_body, TaskAddProjectRequest)
        
        # TODO: Implement task-project relationship
        # For now, just return the updated task
        db.refresh(task)
        
        return format_success_response(_build_task_response(task))
    
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


@router.post("/tasks/{task_gid}/removeProject", response_model=dict)
async def remove_task_from_project(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Remove a task from a project.
    
    Removes the task from the specified project.
    Returns the updated task record.
    Request body must follow OpenAPI spec format: {"data": {"project": "..."}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        remove_project_data = parse_request_body(request_body, TaskRemoveProjectRequest)
        
        # TODO: Implement task-project relationship removal
        # For now, just return the updated task
        db.refresh(task)
        
        return format_success_response(_build_task_response(task))
    
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


@router.post("/tasks/{task_gid}/addTag", response_model=dict)
async def add_tag_to_task(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Add a tag to a task.
    
    Adds a tag to a task.
    Returns the updated task record.
    Request body must follow OpenAPI spec format: {"data": {"tag": "..."}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        add_tag_data = parse_request_body(request_body, TaskAddTagRequest)
        
        # TODO: Implement task-tag relationship
        # For now, just return the updated task
        db.refresh(task)
        
        return format_success_response(_build_task_response(task))
    
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


@router.post("/tasks/{task_gid}/removeTag", response_model=dict)
async def remove_tag_from_task(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Remove a tag from a task.
    
    Removes a tag from a task.
    Returns the updated task record.
    Request body must follow OpenAPI spec format: {"data": {"tag": "..."}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        remove_tag_data = parse_request_body(request_body, TaskRemoveTagRequest)
        
        # TODO: Implement task-tag relationship removal
        # For now, just return the updated task
        db.refresh(task)
        
        return format_success_response(_build_task_response(task))
    
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


@router.post("/tasks/{task_gid}/addFollowers", response_model=dict)
async def add_followers_to_task(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Add followers to a task.
    
    Adds the specified list of users as followers to the task.
    Returns the updated task record.
    Request body must follow OpenAPI spec format: {"data": {"followers": "..."}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        add_followers_data = parse_request_body(request_body, AddFollowersRequest)
        
        # TODO: Implement task-follower relationship
        # For now, just return the updated task
        db.refresh(task)
        
        return format_success_response(_build_task_response(task))
    
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


@router.post("/tasks/{task_gid}/removeFollowers", response_model=dict)
async def remove_followers_from_task(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Remove followers from a task.
    
    Removes the specified list of users from following the task.
    Returns the updated task record.
    Request body must follow OpenAPI spec format: {"data": {"followers": "..."}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        remove_followers_data = parse_request_body(request_body, RemoveFollowersRequest)
        
        # TODO: Implement task-follower relationship removal
        # For now, just return the updated task
        db.refresh(task)
        
        return format_success_response(_build_task_response(task))
    
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


@router.get("/tasks/{task_gid}/subtasks", response_model=dict)
async def get_task_subtasks(
    task_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get subtasks from a task.
    
    Returns a compact representation of all of the subtasks of a task.
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # TODO: Implement task-subtask relationship
        # For now, return empty list
        return format_list_response([])
    
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


@router.get("/tasks/{task_gid}/dependencies", response_model=dict)
async def get_task_dependencies(
    task_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get dependencies from a task.
    
    Returns the compact representations of all of the dependencies of a task.
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # TODO: Implement task-dependency relationship
        # For now, return empty list
        return format_list_response([])
    
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


@router.get("/tasks/{task_gid}/dependents", response_model=dict)
async def get_task_dependents(
    task_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get dependents from a task.
    
    Returns the compact representations of all of the dependents of a task.
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # TODO: Implement task-dependent relationship
        # For now, return empty list
        return format_list_response([])
    
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


@router.get("/tasks/{task_gid}/projects", response_model=dict)
async def get_task_projects(
    task_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get projects a task is in.
    
    Returns a compact representation of all of the projects the task is in.
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # TODO: Implement task-project relationship
        # For now, return empty list
        return format_list_response([])
    
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


@router.get("/tasks/{task_gid}/stories", response_model=dict)
async def get_task_stories(
    task_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get stories from a task.
    
    Returns the compact records for all stories on the task.
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # TODO: Implement task-story relationship
        # For now, return empty list
        return format_list_response([])
    
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


@router.post("/tasks/{task_gid}/stories", response_model=dict)
async def create_task_story(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a story on a task.
    
    Creates a new story on the task.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        from app.schemas.story import StoryCreate
        from app.models.story import Story
        story_data = parse_request_body(request_body, StoryCreate)
        
        # Extract task from data (it's not a direct field on Story model yet)
        story_dict = story_data.model_dump(exclude_unset=True)
        story_dict.pop("task", None)  # Remove task, it's implicit from URL
        
        new_obj = Story(
            gid=str(uuid.uuid4()),
            resource_type="story",
            **story_dict
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        from app.schemas.story import StoryResponse
        obj_response = StoryResponse(
            gid=new_obj.gid,
            resource_type=new_obj.resource_type,
            created_at=new_obj.created_at,
            updated_at=new_obj.updated_at,
            resource_subtype=new_obj.resource_subtype,
            text=new_obj.text,
            html_text=new_obj.html_text,
            is_pinned=new_obj.is_pinned,
            sticker_name=new_obj.sticker_name,
            type=new_obj.type,
            is_editable=new_obj.is_editable,
            is_edited=new_obj.is_edited,
            hearted=new_obj.hearted,
            num_hearts=new_obj.num_hearts,
            liked=new_obj.liked,
            num_likes=new_obj.num_likes,
            old_name=new_obj.old_name,
            new_name=new_obj.new_name,
            old_resource_subtype=new_obj.old_resource_subtype,
            new_resource_subtype=new_obj.new_resource_subtype,
            old_text_value=new_obj.old_text_value,
            new_text_value=new_obj.new_text_value,
            old_number_value=new_obj.old_number_value,
            new_number_value=new_obj.new_number_value,
            new_approval_status=new_obj.new_approval_status,
            old_approval_status=new_obj.old_approval_status,
            source=new_obj.source,
            created_by=None,
            hearts=None,
            likes=None,
            reaction_summary=None,
            previews=None,
            old_dates=None,
            new_dates=None,
            story=None,
            assignee=None,
            follower=None,
            old_section=None,
            new_section=None,
            task=None,
            project=None,
            tag=None,
            custom_field=None,
            old_enum_value=None,
            new_enum_value=None,
            old_date_value=None,
            new_date_value=None,
            old_people_value=None,
            new_people_value=None,
            old_multi_enum_values=None,
            new_multi_enum_values=None,
            duplicate_of=None,
            duplicated_from=None,
            dependency=None,
            target=None
        )
        
        return format_success_response(obj_response, status_code=201)
    
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


@router.get("/tasks/{task_gid}/tags", response_model=dict)
async def get_task_tags(
    task_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a task's tags.
    
    Get a compact representation of all of the tags the task has.
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # TODO: Implement task-tag relationship
        # For now, return empty list
        return format_list_response([])
    
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


@router.get("/tasks/{task_gid}/time_tracking_entries", response_model=dict)
async def get_task_time_tracking_entries(
    task_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get time tracking entries for a task.
    
    Returns time tracking entries for a given task.
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # TODO: Implement task-time_tracking_entry relationship
        # For now, return empty list
        return format_list_response([])
    
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


@router.post("/tasks/{task_gid}/setParent", response_model=dict)
async def set_task_parent(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Set the parent of a task.
    
    Updates the parent of a given task. This endpoint can be used to make a task a subtask of another task, or to remove its existing parent.
    
    When using `insert_before` and `insert_after`, at most one of those two options can be specified, and they must already be subtasks of the parent.
    
    Returns the complete, updated record of the affected task.
    Request body must follow OpenAPI spec format: {"data": {"parent": "...", "insert_before": "...", "insert_after": "..."}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        set_parent_data = parse_request_body(request_body, TaskSetParentRequest)
        
        # TODO: Implement task-parent relationship
        # For now, return the task as-is
        task_response = TaskResponse(
            gid=task.gid,
            resource_type=task.resource_type,
            created_at=task.created_at,
            updated_at=task.updated_at,
            name=task.name,
            resource_subtype=task.resource_subtype,
            created_by=task.created_by,
            approval_status=task.approval_status,
            assignee_status=task.assignee_status,
            completed=task.completed,
            completed_at=task.completed_at,
            due_at=task.due_at,
            due_on=task.due_on,
            external=task.external,
            html_notes=task.html_notes,
            hearted=task.hearted,
            is_rendered_as_separator=task.is_rendered_as_separator,
            liked=task.liked,
            memberships=task.memberships,
            modified_at=task.modified_at,
            notes=task.notes,
            num_hearts=task.num_hearts,
            num_likes=task.num_likes,
            num_subtasks=task.num_subtasks,
            start_at=task.start_at,
            start_on=task.start_on,
            actual_time_minutes=task.actual_time_minutes,
            permalink_url=task.permalink_url,
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
        
        return format_success_response(task_response)
    
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


@router.post("/tasks/{task_gid}/addDependencies", response_model=dict)
async def add_task_dependencies(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Set dependencies for a task.
    
    Marks a set of tasks as dependencies of this task, if they are not already dependencies.
    *A task can have at most 30 dependents and dependencies combined*.
    Request body must follow OpenAPI spec format: {"data": {"dependencies": [...]}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        dependencies_data = parse_request_body(request_body, ModifyDependenciesRequest)
        
        # TODO: Implement task-dependency relationship
        # For now, return EmptyResponse as per OpenAPI spec
        empty_response = EmptyResponse()
        
        return format_success_response(empty_response)
    
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


@router.post("/tasks/{task_gid}/removeDependencies", response_model=dict)
async def remove_task_dependencies(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Unlink dependencies from a task.
    
    Unlinks a set of dependencies from this task.
    Request body must follow OpenAPI spec format: {"data": {"dependencies": [...]}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        dependencies_data = parse_request_body(request_body, ModifyDependenciesRequest)
        
        # TODO: Implement task-dependency relationship removal
        # For now, return EmptyResponse as per OpenAPI spec
        empty_response = EmptyResponse()
        
        return format_success_response(empty_response)
    
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


@router.post("/tasks/{task_gid}/addDependents", response_model=dict)
async def add_task_dependents(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Set dependents for a task.
    
    Marks a set of tasks as dependents of this task, if they are not already dependents.
    *A task can have at most 30 dependents and dependencies combined*.
    Request body must follow OpenAPI spec format: {"data": {"dependents": [...]}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        dependents_data = parse_request_body(request_body, ModifyDependentsRequest)
        
        # TODO: Implement task-dependent relationship
        # For now, return EmptyResponse as per OpenAPI spec
        empty_response = EmptyResponse()
        
        return format_success_response(empty_response)
    
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


@router.post("/tasks/{task_gid}/removeDependents", response_model=dict)
async def remove_task_dependents(
    task_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Unlink dependents from a task.
    
    Unlinks a set of dependents from this task.
    Request body must follow OpenAPI spec format: {"data": {"dependents": [...]}}
    """
    try:
        task = db.query(Task).filter(Task.gid == task_gid).first()
        
        if not task:
            raise NotFoundError("Task", task_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        dependents_data = parse_request_body(request_body, ModifyDependentsRequest)
        
        # TODO: Implement task-dependent relationship removal
        # For now, return EmptyResponse as per OpenAPI spec
        empty_response = EmptyResponse()
        
        return format_success_response(empty_response)
    
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