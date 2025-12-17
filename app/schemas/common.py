"""Common Pydantic schemas used across multiple resources"""
from pydantic import BaseModel, Field
from typing import Optional, List


class EmptyResponse(BaseModel):
    """Empty response schema for endpoints that return no data"""
    pass

    class Config:
        from_attributes = True


class AsanaNamedResource(BaseModel):
    """A generic Asana Resource, containing a globally unique identifier."""
    gid: str = Field(description="Globally unique identifier of the resource, as a string.", example='12345')
    resource_type: str = Field(description="The base type of this resource.", example='task')
    name: Optional[str] = Field(None, description="The name of the resource.", example='Buy catnip')

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


class TaskSetParentRequest(BaseModel):
    """Request schema for setting parent task"""
    parent: Optional[str] = Field(..., description="The new parent of the task, or `null` for no parent.", example='987654')
    insert_after: Optional[str] = Field(None, description="A subtask of the parent to insert the task after, or `null` to insert at the beginning of the list.", example='null')
    insert_before: Optional[str] = Field(None, description="A subtask of the parent to insert the task before, or `null` to insert at the end of the list.", example='124816')

    class Config:
        from_attributes = True


class ModifyDependenciesRequest(BaseModel):
    """Request schema for modifying task dependencies"""
    dependencies: List[str] = Field(description="An array of task gids that a task depends on.", example=['133713', '184253'])

    class Config:
        from_attributes = True


class ModifyDependentsRequest(BaseModel):
    """Request schema for modifying task dependents"""
    dependents: List[str] = Field(description="An array of task gids that are dependents of the given task.", example=['133713', '184253'])

    class Config:
        from_attributes = True


class ProjectSectionInsertRequest(BaseModel):
    """Request schema for inserting/reordering sections in a project"""
    section: str = Field(description="The section to reorder.", example='321654')
    before_section: Optional[str] = Field(None, description="Insert the given section immediately before the section specified by this parameter.", example='86420')
    after_section: Optional[str] = Field(None, description="Insert the given section immediately after the section specified by this parameter.", example='987654')

    class Config:
        from_attributes = True


class AddCustomFieldSettingRequest(BaseModel):
    """Request schema for adding a custom field setting"""
    custom_field: str = Field(description="The custom field to associate with this container.", example='14916')
    is_important: Optional[bool] = Field(None, description="Whether this field should be considered important to this container (for instance, to display in the list view of items in the container).", example=True)
    insert_before: Optional[str] = Field(None, description="A gid of a Custom Field Setting on this container, before which the new Custom Field Setting will be added. `insert_before` and `insert_after` parameters cannot both be specified.", example='1331')
    insert_after: Optional[str] = Field(None, description="A gid of a Custom Field Setting on this container, after which the new Custom Field Setting will be added. `insert_before` and `insert_after` parameters cannot both be specified.", example='1331')

    class Config:
        from_attributes = True


class RemoveCustomFieldSettingRequest(BaseModel):
    """Request schema for removing a custom field setting"""
    custom_field: str = Field(description="The custom field to remove from this portfolio.", example='14916')

    class Config:
        from_attributes = True


class ProjectBriefRequest(BaseModel):
    """Request schema for creating/updating a project brief"""
    title: Optional[str] = Field(None, description="The title of the project brief.", example='Stuff to buy — Project Brief')
    html_text: Optional[str] = Field(None, description="HTML formatted text for the project brief.", example='<body>This is a <strong>project brief</strong>.</body>')
    text: Optional[str] = Field(None, description="The plain text of the project brief. When writing to a project brief, you can specify either `html_text` (preferred) or `text`, but not both.", example='This is a project brief.')

    class Config:
        from_attributes = True


class ProjectSaveAsTemplateRequest(BaseModel):
    """Request schema for saving a project as a template"""
    name: Optional[str] = Field(None, description="The name of the new project template.", example='New Project Template')
    team: Optional[str] = Field(None, description="Sets the team of the new project template.", example='12345')
    public: Optional[bool] = Field(None, description="Sets the public access level of the new project template.", example=False)

    class Config:
        from_attributes = True

