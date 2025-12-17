"""Pydantic schema for Story Response"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class StoryResponse(BaseModel):
    """Story response schema"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.", example='12345')
    resource_type: Optional[str] = Field(description="The base type of this resource.", example='story')
    created_at: Optional[datetime] = Field(description="The time at which this resource was created.", example='2012-02-22T02:06:58.147Z')
    resource_subtype: Optional[str] = Field(description="The subtype of this resource. Different subtypes retain many of the same fields and behavior, but may render differently in Asana or represent resources with different semantic meaning.", example='comment_added')
    text: Optional[str] = Field(description="The plain text of the comment to add. Cannot be used with html_text.", example='This is a comment.')
    html_text: Optional[str] = Field(description="[Opt In](/docs/inputoutput-options). HTML formatted text for a comment. This will not include the name of the creator.", example='<body>This is a comment.</body>')
    is_pinned: Optional[bool] = Field(description="*Conditional*. Whether the story should be pinned on the resource.", example=False)
    sticker_name: Optional[str] = Field(description="The name of the sticker in this story. `null` if there is no sticker.", example='dancing_unicorn')
    created_by: Optional[str] = None
    type: Optional[str] = Field(example='comment')
    is_editable: Optional[bool] = Field(description="*Conditional*. Whether the text of the story can be edited after creation.", example=False)
    is_edited: Optional[bool] = Field(description="*Conditional*. Whether the text of the story has been edited after creation.", example=False)
    hearted: Optional[bool] = Field(description="*Deprecated - please use likes instead* *Conditional*. True if the story is hearted by the authorized user, false if not.", example=False)
    hearts: Optional[List[dict]] = Field(description="*Deprecated - please use likes instead* *Conditional*. Array of likes for users who have hearted this story.")
    num_hearts: Optional[int] = Field(description="*Deprecated - please use likes instead* *Conditional*. The number of users who have hearted this story.", example=5)
    liked: Optional[bool] = Field(description="*Conditional*. True if the story is liked by the authorized user, false if not.", example=False)
    likes: Optional[List[dict]] = Field(description="*Conditional*. Array of likes for users who have liked this story.")
    num_likes: Optional[int] = Field(description="*Conditional*. The number of users who have liked this story.", example=5)
    reaction_summary: Optional[List[dict]] = Field(description="Summary of emoji reactions on this story.")
    previews: Optional[List[dict]] = Field(description="<p><strong style={{ color: \"#4573D2\" }}>Full object requires scope: </strong><code>attachments:read</code></p> *Conditional*. A collection of previews to be displayed in the story. *Note: This property only exists for comment stories.*")
    old_name: Optional[str] = Field(description="*Conditional* The previous name of the task before a name change.", example='This was the old name')
    new_name: Optional[str] = Field(description="*Conditional* The updated name of the task after a name change.", example='This is the new name')
    old_dates: Optional[str] = None
    new_dates: Optional[str] = None
    old_resource_subtype: Optional[str] = Field(description="*Conditional*", example='default_task')
    new_resource_subtype: Optional[str] = Field(description="*Conditional*", example='milestone')
    story: Optional[str] = Field(description="*Conditional*")
    assignee: Optional[str] = Field(description="*Conditional*")
    follower: Optional[str] = Field(description="*Conditional*")
    old_section: Optional[str] = Field(description="*Conditional*")
    new_section: Optional[str] = Field(description="*Conditional*")
    task: Optional[str] = Field(description="*Conditional*")
    project: Optional[str] = Field(description="*Conditional*")
    tag: Optional[str] = Field(description="*Conditional*")
    custom_field: Optional[str] = Field(description="*Conditional*")
    old_text_value: Optional[str] = Field(description="*Conditional* The previous value of a text-type field before it was updated.", example='This was the old text')
    new_text_value: Optional[str] = Field(description="*Conditional* The new value of a text-type field after it was updated.", example='This is the new text')
    old_number_value: Optional[int] = Field(description="*Conditional* The previous value of a number-type custom field before the update.", example=1)
    new_number_value: Optional[int] = Field(description="*Conditional* The new value of a number-type custom field after the update.", example=2)
    old_enum_value: Optional[str] = Field(description="*Conditional*")
    new_enum_value: Optional[str] = Field(description="*Conditional*")
    old_date_value: Optional['StoryCompact'] = None
    new_date_value: Optional['StoryCompact'] = None
    old_people_value: Optional[List['UserCompact']] = Field(description="*Conditional*. The old value of a people custom field story.")
    new_people_value: Optional[List['UserCompact']] = Field(description="*Conditional*. The new value of a people custom field story.")
    old_multi_enum_values: Optional[List[dict]] = Field(description="*Conditional*. The old value of a multi-enum custom field story.")
    new_multi_enum_values: Optional[List[dict]] = Field(description="*Conditional*. The new value of a multi-enum custom field story.")
    new_approval_status: Optional[str] = Field(description="*Conditional*. The new value of approval status.", example='approved')
    old_approval_status: Optional[str] = Field(description="*Conditional*. The old value of approval status.", example='pending')
    duplicate_of: Optional[str] = Field(description="*Conditional*")
    duplicated_from: Optional[str] = Field(description="*Conditional*")
    dependency: Optional[str] = Field(description="*Conditional*")
    source: Optional[str] = Field(description="The component of the Asana product the user used to trigger the story.", example='web')
    target: Optional['TaskCompact'] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gid": "12345",
                "resource_type": "story",
                "name": "Example Name"
            }
        }

"""Pydantic schema for Story Compact (nested)"""
from pydantic import BaseModel, Field
from typing import Optional


class StoryCompact(BaseModel):
    """Story compact schema for nested responses"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.")
    resource_type: Optional[str] = Field(description="The base type of this resource.")

    class Config:
        from_attributes = True

"""Pydantic schema for Story Create Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class StoryCreate(BaseModel):
    """Story create request schema"""

    text: Optional[str] = Field(None, description="The plain text of the comment to add. Cannot be used with html_text.")
    html_text: Optional[str] = Field(None, description="[Opt In](/docs/inputoutput-options). HTML formatted text for a comment. This will not include the name of the creator.")
    is_pinned: Optional[bool] = Field(None, description="*Conditional*. Whether the story should be pinned on the resource.")
    sticker_name: Optional[str] = Field(None, description="The name of the sticker in this story. `null` if there is no sticker.")
    created_by: Optional[str] = None
    old_name: Optional[str] = Field(None, description="*Conditional* The previous name of the task before a name change.")
    old_dates: Optional[str] = None
    new_dates: Optional[str] = None
    target: Optional['TaskCompact'] = None

    class Config:
        from_attributes = True

"""Pydantic schema for Story Update Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class StoryUpdate(BaseModel):
    """Story update request schema"""

    text: Optional[str] = Field(None, description="The plain text of the comment to add. Cannot be used with html_text.")
    html_text: Optional[str] = Field(None, description="[Opt In](/docs/inputoutput-options). HTML formatted text for a comment. This will not include the name of the creator.")
    is_pinned: Optional[bool] = Field(None, description="*Conditional*. Whether the story should be pinned on the resource.")
    sticker_name: Optional[str] = Field(None, description="The name of the sticker in this story. `null` if there is no sticker.")
    created_by: Optional[str] = None
    old_name: Optional[str] = Field(None, description="*Conditional* The previous name of the task before a name change.")
    old_dates: Optional[str] = None
    new_dates: Optional[str] = None
    target: Optional['TaskCompact'] = None

    class Config:
        from_attributes = True