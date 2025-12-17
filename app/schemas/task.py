"""Pydantic schema for Task Response"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class TaskResponse(BaseModel):
    """Task response schema"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.", example='12345')
    resource_type: Optional[str] = Field(description="The base type of this resource.", example='task')
    name: Optional[str] = Field(description="Name of the task. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.", example='Buy catnip')
    resource_subtype: Optional[str] = Field(description="The subtype of this resource. Different subtypes retain many of the same fields and behavior, but may render differently in Asana or represent resources with different semantic meaning. The resource_subtype `milestone` represent a single moment in time. This means tasks with this subtype cannot have a start_date.", example='default_task')
    created_by: Optional[dict] = Field(description="[Opt In](/docs/inputoutput-options). A *user* object represents an account in Asana that can be given access to various workspaces, projects, and tasks.")
    approval_status: Optional[str] = Field(description="*Conditional* Reflects the approval status of this task. This field is kept in sync with `completed`, meaning `pending` translates to false while `approved`, `rejected`, and `changes_requested` translate to true. If you set completed to true, this field will be set to `approved`.", example='pending')
    assignee_status: Optional[str] = Field(description="*Deprecated* Scheduling status of this task for the user it is assigned to. This field can only be set if the assignee is non-null. Setting this field to \"inbox\" or \"upcoming\" inserts it at the top of the section, while the other options will insert at the bottom.", example='upcoming')
    completed: Optional[bool] = Field(description="True if the task is currently marked complete, false if not.", example=False)
    completed_at: Optional[datetime] = Field(description="The time at which this task was completed, or null if the task is incomplete.", example='2012-02-22T02:06:58.147Z')
    completed_by: Optional['UserCompact'] = None
    created_at: Optional[datetime] = Field(description="The time at which this resource was created.", example='2012-02-22T02:06:58.147Z')
    dependencies: Optional[List[dict]] = Field(description="[Opt In](/docs/inputoutput-options). Array of resources referencing tasks that this task depends on. The objects contain only the gid of the dependency.")
    dependents: Optional[List[dict]] = Field(description="[Opt In](/docs/inputoutput-options). Array of resources referencing tasks that depend on this task. The objects contain only the ID of the dependent.")
    due_at: Optional[datetime] = Field(description="The UTC date and time on which this task is due, or null if the task has no due time. This takes an ISO 8601 date string in UTC and should not be used together with `due_on`.", example='2019-09-15T02:06:58.147Z')
    due_on: Optional[date] = Field(description="The localized date on which this task is due, or null if the task has no due date. This takes a date with `YYYY-MM-DD` format and should not be used together with `due_at`.", example='2019-09-15')
    external: Optional[dict] = Field(description="*OAuth Required*. *Conditional*. This field is returned only if external values are set or included by using [Opt In] (/docs/inputoutput-options). The external field allows you to store app-specific metadata on tasks, including a gid that can be used to retrieve tasks and a data blob that can store app-specific character strings. Note that you will need to authenticate with Oauth to access or modify this data. Once an external gid is set, you can use the notation `external:custom_gid` to reference your object anywhere in the API where you may use the original object gid. See the page on Custom External Data for more details.", example={'gid': 'my_gid', 'data': 'A blob of information'})
    html_notes: Optional[str] = Field(description="[Opt In](/docs/inputoutput-options). The notes of the text with formatting as HTML.", example='<body>Mittens <em>really</em> likes the stuff from Humboldt.</body>')
    hearted: Optional[bool] = Field(description="*Deprecated - please use liked instead* True if the task is hearted by the authorized user, false if not.", example=True)
    hearts: Optional[List[dict]] = Field(description="*Deprecated - please use likes instead* Array of likes for users who have hearted this task.")
    is_rendered_as_separator: Optional[bool] = Field(description="[Opt In](/docs/inputoutput-options). In some contexts tasks can be rendered as a visual separator; for instance, subtasks can appear similar to [sections](/reference/sections) without being true `section` objects. If a `task` object is rendered this way in any context it will have the property `is_rendered_as_separator` set to `true`. This parameter only applies to regular tasks with `resource_subtype` of `default_task`. Tasks with `resource_subtype` of `milestone`, `approval`, or custom task types will not have this property and cannot be rendered as separators.", example=False)
    liked: Optional[bool] = Field(description="True if the task is liked by the authorized user, false if not.", example=True)
    likes: Optional[List[dict]] = Field(description="Array of likes for users who have liked this task.")
    memberships: Optional[List[dict]] = Field(description="<p><strong style={{ color: \"#4573D2\" }}>Full object requires scope: </strong><code>projects:read</code>, <code>project_sections:read</code></p> *Create-only*. Array of projects this task is associated with and the section it is in. At task creation time, this array can be used to add the task to specific sections. After task creation, these associations can be modified using the `addProject` and `removeProject` endpoints. Note that over time, more types of memberships may be added to this property.")
    modified_at: Optional[datetime] = Field(description="The time at which this task was last modified. The following conditions will change `modified_at`: - story is created on a task - story is trashed on a task - attachment is trashed on a task - task is assigned or unassigned - custom field value is changed - the task itself is trashed - Or if any of the following fields are updated: - completed - name - due_date - description - attachments - items - schedule_status The following conditions will _not_ change `modified_at`: - moving to a new container (project, portfolio, etc) - comments being added to the task (but the stories they generate _will_ affect `modified_at`)", example='2012-02-22T02:06:58.147Z')
    notes: Optional[str] = Field(description="Free-form textual information associated with the task (i.e. its description).", example='Mittens really likes the stuff from Humboldt.')
    num_hearts: Optional[int] = Field(description="*Deprecated - please use likes instead* The number of users who have hearted this task.", example=5)
    num_likes: Optional[int] = Field(description="The number of users who have liked this task.", example=5)
    num_subtasks: Optional[int] = Field(description="[Opt In](/docs/inputoutput-options). The number of subtasks on this task.", example=3)
    start_at: Optional[datetime] = Field(description="Date and time on which work begins for the task, or null if the task has no start time. This takes an ISO 8601 date string in UTC and should not be used together with `start_on`. *Note: `due_at` must be present in the request when setting or unsetting the `start_at` parameter.*", example='2019-09-14T02:06:58.147Z')
    start_on: Optional[date] = Field(description="The day on which work begins for the task , or null if the task has no start date. This takes a date with `YYYY-MM-DD` format and should not be used together with `start_at`. *Note: `due_on` or `due_at` must be present in the request when setting or unsetting the `start_on` parameter.*", example='2019-09-14')
    actual_time_minutes: Optional[float] = Field(description="<p><strong style={{ color: \"#4573D2\" }}>Full object requires scope: </strong><code>time_tracking_entries:read</code></p> This value represents the sum of all the Time Tracking entries in the Actual Time field on a given Task. It is represented as a nullable long value.", example=200)
    assignee: Optional['UserCompact'] = None
    assignee_section: Optional['SectionCompact'] = None
    custom_fields: Optional[List['CustomFieldCompact']] = Field(description="Array of custom field values applied to the task. These represent the custom field values recorded on this project for a particular custom field. For example, these custom field values will contain an `enum_value` property for custom fields of type `enum`, a `text_value` property for custom fields of type `text`, and so on. Please note that the `gid` returned on each custom field value *is identical* to the `gid` of the custom field, which allows referencing the custom field metadata through the `/custom_fields/custom_field_gid` endpoint.")
    custom_type: Optional[dict] = None
    custom_type_status_option: Optional[dict] = None
    followers: Optional[List['UserCompact']] = Field(description="Array of users following this task.")
    parent: Optional['TaskCompact'] = None
    projects: Optional[List['ProjectCompact']] = Field(description="*Create-only.* Array of projects this task is associated with. At task creation time, this array can be used to add the task to many projects at once. After task creation, these associations can be modified using the addProject and removeProject endpoints.")
    tags: Optional[List['TagCompact']] = Field(description="Array of tags associated with this task. In order to change tags on an existing task use `addTag` and `removeTag`.", example=[{'gid': '59746', 'name': 'Grade A'}])
    workspace: Optional['WorkspaceCompact'] = None
    permalink_url: Optional[str] = Field(description="A url that points directly to the object within Asana.", example='https://app.asana.com/1/12345/task/123456789')

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gid": "12345",
                "resource_type": "task",
                "name": "Example Name"
            }
        }

"""Pydantic schema for Task Compact (nested)"""
from pydantic import BaseModel, Field
from typing import Optional


class TaskCompact(BaseModel):
    """Task compact schema for nested responses"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.")
    resource_type: Optional[str] = Field(description="The base type of this resource.")
    name: str = Field(description="The name of the task.")

    class Config:
        from_attributes = True

"""Pydantic schema for Task Create Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class TaskCreate(BaseModel):
    """Task create request schema"""

    name: Optional[str] = Field(None, description="Name of the task. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")
    resource_subtype: Optional[str] = Field(None, description="The subtype of this resource. Different subtypes retain many of the same fields and behavior, but may render differently in Asana or represent resources with different semantic meaning. The resource_subtype `milestone` represent a single moment in time. This means tasks with this subtype cannot have a start_date.")
    approval_status: Optional[str] = Field(None, description="*Conditional* Reflects the approval status of this task. This field is kept in sync with `completed`, meaning `pending` translates to false while `approved`, `rejected`, and `changes_requested` translate to true. If you set completed to true, this field will be set to `approved`.")
    assignee_status: Optional[str] = Field(None, description="*Deprecated* Scheduling status of this task for the user it is assigned to. This field can only be set if the assignee is non-null. Setting this field to \"inbox\" or \"upcoming\" inserts it at the top of the section, while the other options will insert at the bottom.")
    completed: Optional[bool] = Field(None, description="True if the task is currently marked complete, false if not.")
    completed_by: Optional['UserCompact'] = None
    due_at: Optional[datetime] = Field(None, description="The UTC date and time on which this task is due, or null if the task has no due time. This takes an ISO 8601 date string in UTC and should not be used together with `due_on`.")
    due_on: Optional[date] = Field(None, description="The localized date on which this task is due, or null if the task has no due date. This takes a date with `YYYY-MM-DD` format and should not be used together with `due_at`.")
    external: Optional[dict] = Field(None, description="*OAuth Required*. *Conditional*. This field is returned only if external values are set or included by using [Opt In] (/docs/inputoutput-options). The external field allows you to store app-specific metadata on tasks, including a gid that can be used to retrieve tasks and a data blob that can store app-specific character strings. Note that you will need to authenticate with Oauth to access or modify this data. Once an external gid is set, you can use the notation `external:custom_gid` to reference your object anywhere in the API where you may use the original object gid. See the page on Custom External Data for more details.")
    html_notes: Optional[str] = Field(None, description="[Opt In](/docs/inputoutput-options). The notes of the text with formatting as HTML.")
    liked: Optional[bool] = Field(None, description="True if the task is liked by the authorized user, false if not.")
    notes: Optional[str] = Field(None, description="Free-form textual information associated with the task (i.e. its description).")
    start_at: Optional[datetime] = Field(None, description="Date and time on which work begins for the task, or null if the task has no start time. This takes an ISO 8601 date string in UTC and should not be used together with `start_on`. *Note: `due_at` must be present in the request when setting or unsetting the `start_at` parameter.*")
    start_on: Optional[date] = Field(None, description="The day on which work begins for the task , or null if the task has no start date. This takes a date with `YYYY-MM-DD` format and should not be used together with `start_at`. *Note: `due_on` or `due_at` must be present in the request when setting or unsetting the `start_on` parameter.*")
    assignee: Optional['UserCompact'] = None
    assignee_section: Optional['SectionCompact'] = None
    custom_type: Optional[dict] = None
    custom_type_status_option: Optional[dict] = None
    parent: Optional['TaskCompact'] = None
    workspace: Optional['WorkspaceCompact'] = None

    class Config:
        from_attributes = True

"""Pydantic schema for Task Update Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class TaskUpdate(BaseModel):
    """Task update request schema"""

    name: Optional[str] = Field(None, description="Name of the task. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")
    resource_subtype: Optional[str] = Field(None, description="The subtype of this resource. Different subtypes retain many of the same fields and behavior, but may render differently in Asana or represent resources with different semantic meaning. The resource_subtype `milestone` represent a single moment in time. This means tasks with this subtype cannot have a start_date.")
    approval_status: Optional[str] = Field(None, description="*Conditional* Reflects the approval status of this task. This field is kept in sync with `completed`, meaning `pending` translates to false while `approved`, `rejected`, and `changes_requested` translate to true. If you set completed to true, this field will be set to `approved`.")
    assignee_status: Optional[str] = Field(None, description="*Deprecated* Scheduling status of this task for the user it is assigned to. This field can only be set if the assignee is non-null. Setting this field to \"inbox\" or \"upcoming\" inserts it at the top of the section, while the other options will insert at the bottom.")
    completed: Optional[bool] = Field(None, description="True if the task is currently marked complete, false if not.")
    completed_by: Optional['UserCompact'] = None
    due_at: Optional[datetime] = Field(None, description="The UTC date and time on which this task is due, or null if the task has no due time. This takes an ISO 8601 date string in UTC and should not be used together with `due_on`.")
    due_on: Optional[date] = Field(None, description="The localized date on which this task is due, or null if the task has no due date. This takes a date with `YYYY-MM-DD` format and should not be used together with `due_at`.")
    external: Optional[dict] = Field(None, description="*OAuth Required*. *Conditional*. This field is returned only if external values are set or included by using [Opt In] (/docs/inputoutput-options). The external field allows you to store app-specific metadata on tasks, including a gid that can be used to retrieve tasks and a data blob that can store app-specific character strings. Note that you will need to authenticate with Oauth to access or modify this data. Once an external gid is set, you can use the notation `external:custom_gid` to reference your object anywhere in the API where you may use the original object gid. See the page on Custom External Data for more details.")
    html_notes: Optional[str] = Field(None, description="[Opt In](/docs/inputoutput-options). The notes of the text with formatting as HTML.")
    liked: Optional[bool] = Field(None, description="True if the task is liked by the authorized user, false if not.")
    notes: Optional[str] = Field(None, description="Free-form textual information associated with the task (i.e. its description).")
    start_at: Optional[datetime] = Field(None, description="Date and time on which work begins for the task, or null if the task has no start time. This takes an ISO 8601 date string in UTC and should not be used together with `start_on`. *Note: `due_at` must be present in the request when setting or unsetting the `start_at` parameter.*")
    start_on: Optional[date] = Field(None, description="The day on which work begins for the task , or null if the task has no start date. This takes a date with `YYYY-MM-DD` format and should not be used together with `start_at`. *Note: `due_on` or `due_at` must be present in the request when setting or unsetting the `start_on` parameter.*")
    assignee: Optional['UserCompact'] = None
    assignee_section: Optional['SectionCompact'] = None
    custom_type: Optional[dict] = None
    custom_type_status_option: Optional[dict] = None
    parent: Optional['TaskCompact'] = None
    workspace: Optional['WorkspaceCompact'] = None

    class Config:
        from_attributes = True