"""Common Pydantic schemas used across multiple resources"""
from pydantic import BaseModel, Field
from typing import Optional, List


class EmptyResponse(BaseModel):
    """Empty response schema for endpoints that return no data"""
    pass

    class Config:
        from_attributes = True


class WorkspaceAddUserRequest(BaseModel):
    """Request schema for adding a user to a workspace"""
    user: str = Field(description="A string identifying a user. This can either be the string 'me', an email, or the gid of a user.", example='12345')

    class Config:
        from_attributes = True


class WorkspaceRemoveUserRequest(BaseModel):
    """Request schema for removing a user from a workspace"""
    user: str = Field(description="A string identifying a user. This can either be the string 'me', an email, or the gid of a user.", example='12345')

    class Config:
        from_attributes = True


class AddMembersRequest(BaseModel):
    """Request schema for adding members to a project/team"""
    members: List[str] = Field(description="An array of strings identifying users. These can either be the string 'me', an email, or the gid of a user.", example=['521621', '621373'])

    class Config:
        from_attributes = True


class RemoveMembersRequest(BaseModel):
    """Request schema for removing members from a project/team"""
    members: List[str] = Field(description="An array of strings identifying users. These can either be the string 'me', an email, or the gid of a user.", example=['521621', '621373'])

    class Config:
        from_attributes = True


class AddFollowersRequest(BaseModel):
    """Request schema for adding followers to a project/task"""
    followers: List[str] = Field(description="An array of strings identifying users. These can either be the string 'me', an email, or the gid of a user.", example=['521621', '621373'])

    class Config:
        from_attributes = True


class RemoveFollowersRequest(BaseModel):
    """Request schema for removing followers from a project/task"""
    followers: List[str] = Field(description="An array of strings identifying users. These can either be the string 'me', an email, or the gid of a user.", example=['521621', '621373'])

    class Config:
        from_attributes = True


class ProjectDuplicateRequest(BaseModel):
    """Request schema for duplicating a project"""
    name: str = Field(description="The name of the new project.", example='New Project Name')
    team: Optional[str] = Field(None, description="Sets the team of the new project. If team is not defined, the new project will be in the same team as the the original project.", example='12345')
    include: Optional[str] = Field(None, description="A comma-separated list of elements to include when duplicating a project.", example='members,notes')

    class Config:
        from_attributes = True


class TaskDuplicateRequest(BaseModel):
    """Request schema for duplicating a task"""
    name: Optional[str] = Field(None, description="The name of the new task.", example='New Task Name')
    include: Optional[str] = Field(None, description="A comma-separated list of fields that will be duplicated to the new task.", example='assignee,attachments,notes')

    class Config:
        from_attributes = True


class TaskAddProjectRequest(BaseModel):
    """Request schema for adding a task to a project"""
    project: str = Field(description="The project to add the task to.", example='13579')
    insert_after: Optional[str] = Field(None, description="A task in the project to insert the task after, or null to insert at the beginning of the list.", example='124816')
    insert_before: Optional[str] = Field(None, description="A task in the project to insert the task before, or null to insert at the end of the list.", example='124816')

    class Config:
        from_attributes = True


class TaskRemoveProjectRequest(BaseModel):
    """Request schema for removing a task from a project"""
    project: str = Field(description="The project to remove the task from.", example='13579')

    class Config:
        from_attributes = True


class TaskAddTagRequest(BaseModel):
    """Request schema for adding a tag to a task"""
    tag: str = Field(description="The tag's gid to add to the task.", example='13579')

    class Config:
        from_attributes = True


class TaskRemoveTagRequest(BaseModel):
    """Request schema for removing a tag from a task"""
    tag: str = Field(description="The tag's gid to remove from the task.", example='13579')

    class Config:
        from_attributes = True


class TeamAddUserRequest(BaseModel):
    """Request schema for adding a user to a team"""
    user: str = Field(description="A string identifying a user. This can either be the string 'me', an email, or the gid of a user.", example='12345')

    class Config:
        from_attributes = True


class TeamRemoveUserRequest(BaseModel):
    """Request schema for removing a user from a team"""
    user: str = Field(description="A string identifying a user. This can either be the string 'me', an email, or the gid of a user.", example='12345')

    class Config:
        from_attributes = True


class SectionAddTaskRequest(BaseModel):
    """Request schema for adding a task to a section"""
    task: str = Field(description="The task to add to this section.", example='12345')
    insert_before: Optional[str] = Field(None, description="An existing task within this section before which the new task should be inserted. Cannot be provided together with insert_after.", example='124816')
    insert_after: Optional[str] = Field(None, description="An existing task within this section after which the new task should be inserted. Cannot be provided together with insert_before.", example='124816')

    class Config:
        from_attributes = True


class EnumOptionRequest(BaseModel):
    """Request schema for creating an enum option"""
    name: str = Field(description="The name of the enum option.", example='Low')
    enabled: Optional[bool] = Field(True, description="Whether or not the enum option is a selectable value for the custom field.", example=True)
    color: Optional[str] = Field(None, description="The color of the enum option. Defaults to 'none'.", example='blue')
    insert_before: Optional[str] = Field(None, description="An existing enum option within this custom field before which the new enum option should be inserted. Cannot be provided together with insert_after.", example='12345')
    insert_after: Optional[str] = Field(None, description="An existing enum option within this custom field after which the new enum option should be inserted. Cannot be provided together with insert_before.", example='12345')

    class Config:
        from_attributes = True


class EnumOptionInsertRequest(BaseModel):
    """Request schema for reordering enum options"""
    enum_option: str = Field(description="The gid of the enum option to relocate.", example='97285')
    before_enum_option: Optional[str] = Field(None, description="An existing enum option within this custom field before which the new enum option should be inserted. Cannot be provided together with after_enum_option.", example='12345')
    after_enum_option: Optional[str] = Field(None, description="An existing enum option within this custom field after which the new enum option should be inserted. Cannot be provided together with before_enum_option.", example='12345')

    class Config:
        from_attributes = True

