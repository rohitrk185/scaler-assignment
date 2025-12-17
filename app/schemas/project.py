"""Pydantic schema for Project Response"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class ProjectResponse(BaseModel):
    """Project response schema"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.", example='12345')
    resource_type: Optional[str] = Field(description="The base type of this resource.", example='project')
    name: Optional[str] = Field(description="Name of the project. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.", example='Stuff to buy')
    archived: Optional[bool] = Field(description="True if the project is archived, false if not. Archived projects do not show in the UI by default and may be treated differently for queries.", example=False)
    color: Optional[str] = Field(description="Color of the project.", example='light-green')
    icon: Optional[str] = Field(description="The icon for a project.", example='chat_bubbles')
    created_at: Optional[datetime] = Field(description="The time at which this resource was created.", example='2012-02-22T02:06:58.147Z')
    current_status: Optional['ProjectCompact'] = None
    current_status_update: Optional[dict] = None
    custom_field_settings: Optional[List['CustomFieldCompact']] = Field(description="<p><strong style={{ color: \"#4573D2\" }}>Full object requires scope: </strong><code>custom_fields:read</code></p> Array of Custom Field Settings (in compact form).")
    default_view: Optional[str] = Field(description="The default view (list, board, calendar, or timeline) of a project.", example='calendar')
    due_date: Optional[date] = Field(description="*Deprecated: new integrations should prefer the `due_on` field.*", example='2019-09-15')
    due_on: Optional[date] = Field(description="The day on which this project is due. This takes a date with format YYYY-MM-DD.", example='2019-09-15')
    html_notes: Optional[str] = Field(description="[Opt In](/docs/inputoutput-options). The notes of the project with formatting as HTML.", example='<body>These are things we need to purchase.</body>')
    members: Optional[List['UserCompact']] = Field(description="Array of users who are members of this project.")
    modified_at: Optional[datetime] = Field(description="The time at which this project was last modified. *Note: This does not currently reflect any changes in associations such as tasks or comments that may have been added or removed from the project.*", example='2012-02-22T02:06:58.147Z')
    notes: Optional[str] = Field(description="Free-form textual information associated with the project (ie., its description).", example='These are things we need to purchase.')
    public: Optional[bool] = Field(description="*Deprecated:* new integrations use `privacy_setting` instead.", example=False)
    privacy_setting: Optional[str] = Field(description="The privacy setting of the project. *Note: Administrators in your organization may restrict the values of `privacy_setting`.*", example='public_to_workspace')
    start_on: Optional[date] = Field(description="The day on which work for this project begins, or null if the project has no start date. This takes a date with `YYYY-MM-DD` format. *Note: `due_on` or `due_at` must be present in the request when setting or unsetting the `start_on` parameter. Additionally, `start_on` and `due_on` cannot be the same date.*", example='2019-09-14')
    default_access_level: Optional[str] = Field(description="The default access for users or teams who join or are added as members to the project.", example='admin')
    minimum_access_level_for_customization: Optional[str] = Field(description="The minimum access level needed for project members to modify this project's workflow and appearance.", example='admin')
    minimum_access_level_for_sharing: Optional[str] = Field(description="The minimum access level needed for project members to share the project and manage project memberships.", example='admin')
    custom_fields: Optional[List['CustomFieldCompact']] = Field(description="Array of Custom Fields.")
    completed: Optional[bool] = Field(description="True if the project is currently marked complete, false if not.", example=False)
    completed_at: Optional[datetime] = Field(description="The time at which this project was completed, or null if the project is not completed.", example='2012-02-22T02:06:58.147Z')
    completed_by: Optional['UserCompact'] = None
    followers: Optional[List['UserCompact']] = Field(description="Array of users following this project. Followers are a subset of members who have opted in to receive \"tasks added\" notifications for a project.")
    owner: Optional['UserCompact'] = Field(description="The current owner of the project, may be null.")
    team: Optional['TeamCompact'] = None
    permalink_url: Optional[str] = Field(description="A url that points directly to the object within Asana.", example='https://app.asana.com/1/12345/project/123456789')
    project_brief: Optional['ProjectCompact'] = None
    created_from_template: Optional['ProjectCompact'] = None
    workspace: Optional['WorkspaceCompact'] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gid": "12345",
                "resource_type": "project",
                "name": "Example Name"
            }
        }

"""Pydantic schema for Project Compact (nested)"""
from pydantic import BaseModel, Field
from typing import Optional


class ProjectCompact(BaseModel):
    """Project compact schema for nested responses"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.")
    resource_type: Optional[str] = Field(description="The base type of this resource.")
    name: str = Field(description="Name of the project. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")

    class Config:
        from_attributes = True

"""Pydantic schema for Project Create Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class ProjectCreate(BaseModel):
    """Project create request schema"""

    name: Optional[str] = Field(None, max_length=256, description="Name of the project. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")
    archived: Optional[bool] = Field(None, description="True if the project is archived, false if not. Archived projects do not show in the UI by default and may be treated differently for queries.")
    color: Optional[str] = Field(None, description="Color of the project.")
    icon: Optional[str] = Field(None, description="The icon for a project.")
    current_status: Optional['ProjectCompact'] = None
    current_status_update: Optional[dict] = None
    default_view: Optional[str] = Field(None, description="The default view (list, board, calendar, or timeline) of a project.")
    due_date: Optional[date] = Field(None, description="*Deprecated: new integrations should prefer the `due_on` field.*")
    due_on: Optional[date] = Field(None, description="The day on which this project is due. This takes a date with format YYYY-MM-DD.")
    html_notes: Optional[str] = Field(None, description="[Opt In](/docs/inputoutput-options). The notes of the project with formatting as HTML.")
    notes: Optional[str] = Field(None, description="Free-form textual information associated with the project (ie., its description).")
    public: Optional[bool] = Field(None, description="*Deprecated:* new integrations use `privacy_setting` instead.")
    privacy_setting: Optional[str] = Field(None, description="The privacy setting of the project. *Note: Administrators in your organization may restrict the values of `privacy_setting`.*")
    start_on: Optional[date] = Field(None, description="The day on which work for this project begins, or null if the project has no start date. This takes a date with `YYYY-MM-DD` format. *Note: `due_on` or `due_at` must be present in the request when setting or unsetting the `start_on` parameter. Additionally, `start_on` and `due_on` cannot be the same date.*")
    default_access_level: Optional[str] = Field(None, description="The default access for users or teams who join or are added as members to the project.")
    minimum_access_level_for_customization: Optional[str] = Field(None, description="The minimum access level needed for project members to modify this project's workflow and appearance.")
    minimum_access_level_for_sharing: Optional[str] = Field(None, description="The minimum access level needed for project members to share the project and manage project memberships.")
    completed_by: Optional['UserCompact'] = None
    owner: Optional['UserCompact'] = Field(None, description="The current owner of the project, may be null.")
    team: Optional['TeamCompact'] = None
    project_brief: Optional['ProjectCompact'] = None
    created_from_template: Optional['ProjectCompact'] = None
    workspace: Optional['WorkspaceCompact'] = None

    class Config:
        from_attributes = True

"""Pydantic schema for Project Update Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class ProjectUpdate(BaseModel):
    """Project update request schema"""

    name: Optional[str] = Field(None, max_length=256, description="Name of the project. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")
    archived: Optional[bool] = Field(None, description="True if the project is archived, false if not. Archived projects do not show in the UI by default and may be treated differently for queries.")
    color: Optional[str] = Field(None, description="Color of the project.")
    icon: Optional[str] = Field(None, description="The icon for a project.")
    current_status: Optional['ProjectCompact'] = None
    current_status_update: Optional[dict] = None
    default_view: Optional[str] = Field(None, description="The default view (list, board, calendar, or timeline) of a project.")
    due_date: Optional[date] = Field(None, description="*Deprecated: new integrations should prefer the `due_on` field.*")
    due_on: Optional[date] = Field(None, description="The day on which this project is due. This takes a date with format YYYY-MM-DD.")
    html_notes: Optional[str] = Field(None, description="[Opt In](/docs/inputoutput-options). The notes of the project with formatting as HTML.")
    notes: Optional[str] = Field(None, description="Free-form textual information associated with the project (ie., its description).")
    public: Optional[bool] = Field(None, description="*Deprecated:* new integrations use `privacy_setting` instead.")
    privacy_setting: Optional[str] = Field(None, description="The privacy setting of the project. *Note: Administrators in your organization may restrict the values of `privacy_setting`.*")
    start_on: Optional[date] = Field(None, description="The day on which work for this project begins, or null if the project has no start date. This takes a date with `YYYY-MM-DD` format. *Note: `due_on` or `due_at` must be present in the request when setting or unsetting the `start_on` parameter. Additionally, `start_on` and `due_on` cannot be the same date.*")
    default_access_level: Optional[str] = Field(None, description="The default access for users or teams who join or are added as members to the project.")
    minimum_access_level_for_customization: Optional[str] = Field(None, description="The minimum access level needed for project members to modify this project's workflow and appearance.")
    minimum_access_level_for_sharing: Optional[str] = Field(None, description="The minimum access level needed for project members to share the project and manage project memberships.")
    completed_by: Optional['UserCompact'] = None
    owner: Optional['UserCompact'] = Field(None, description="The current owner of the project, may be null.")
    team: Optional['TeamCompact'] = None
    project_brief: Optional['ProjectCompact'] = None
    created_from_template: Optional['ProjectCompact'] = None
    workspace: Optional['WorkspaceCompact'] = None

    class Config:
        from_attributes = True