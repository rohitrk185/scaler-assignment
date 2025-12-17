"""Pydantic schema for Team Response"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class TeamResponse(BaseModel):
    """Team response schema"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.", example='12345')
    resource_type: Optional[str] = Field(description="The base type of this resource.", example='team')
    name: Optional[str] = Field(description="The name of the team.", example='Marketing')
    description: Optional[str] = Field(description="[Opt In](/docs/inputoutput-options). The description of the team.", example='All developers should be members of this team.')
    html_description: Optional[str] = Field(description="[Opt In](/docs/inputoutput-options). The description of the team with formatting as HTML.", example='<body><em>All</em> developers should be members of this team.</body>')
    organization: Optional['WorkspaceCompact'] = None
    permalink_url: Optional[str] = Field(description="A url that points directly to the object within Asana.", example='https://app.asana.com/0/resource/123456789/list')
    visibility: Optional[str] = Field(description="The visibility of the team to users in the same organization")
    edit_team_name_or_description_access_level: Optional[str] = Field(description="Controls who can edit team name and description")
    edit_team_visibility_or_trash_team_access_level: Optional[str] = Field(description="Controls who can edit team visibility and trash teams")
    member_invite_management_access_level: Optional[str] = Field(description="Controls who can accept or deny member invites for a given team")
    guest_invite_management_access_level: Optional[str] = Field(description="Controls who can accept or deny guest invites for a given team")
    join_request_management_access_level: Optional[str] = Field(description="Controls who can accept or deny join team requests for a Membership by Request team. This field can only be updated when the team's `visibility` field is `request_to_join`.")
    team_member_removal_access_level: Optional[str] = Field(description="Controls who can remove team members")
    team_content_management_access_level: Optional[str] = Field(description="Controls who can create and share content with the team")
    endorsed: Optional[bool] = Field(description="Whether the team has been endorsed", example=False)
    custom_field_settings: Optional[List['CustomFieldCompact']] = Field(description="Array of Custom Field Settings applied to the team.")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gid": "12345",
                "resource_type": "team",
                "name": "Example Name"
            }
        }

"""Pydantic schema for Team Compact (nested)"""
from pydantic import BaseModel, Field
from typing import Optional


class TeamCompact(BaseModel):
    """Team compact schema for nested responses"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.")
    resource_type: Optional[str] = Field(description="The base type of this resource.")
    name: str = Field(description="The name of the team.")

    class Config:
        from_attributes = True

"""Pydantic schema for Team Create Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class TeamCreate(BaseModel):
    """Team create request schema"""

    name: Optional[str] = Field(None, description="The name of the team.")
    description: Optional[str] = Field(None, description="[Opt In](/docs/inputoutput-options). The description of the team.")
    html_description: Optional[str] = Field(None, description="[Opt In](/docs/inputoutput-options). The description of the team with formatting as HTML.")
    organization: Optional['WorkspaceCompact'] = None
    visibility: Optional[str] = Field(None, description="The visibility of the team to users in the same organization")
    edit_team_name_or_description_access_level: Optional[str] = Field(None, description="Controls who can edit team name and description")
    edit_team_visibility_or_trash_team_access_level: Optional[str] = Field(None, description="Controls who can edit team visibility and trash teams")
    member_invite_management_access_level: Optional[str] = Field(None, description="Controls who can accept or deny member invites for a given team")
    guest_invite_management_access_level: Optional[str] = Field(None, description="Controls who can accept or deny guest invites for a given team")
    join_request_management_access_level: Optional[str] = Field(None, description="Controls who can accept or deny join team requests for a Membership by Request team. This field can only be updated when the team's `visibility` field is `request_to_join`.")
    team_member_removal_access_level: Optional[str] = Field(None, description="Controls who can remove team members")
    team_content_management_access_level: Optional[str] = Field(None, description="Controls who can create and share content with the team")
    endorsed: Optional[bool] = Field(None, description="Whether the team has been endorsed")
    custom_field_settings: Optional[List['CustomFieldCompact']] = Field(None, description="Array of Custom Field Settings applied to the team.")

    class Config:
        from_attributes = True

"""Pydantic schema for Team Update Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class TeamUpdate(BaseModel):
    """Team update request schema"""

    name: Optional[str] = Field(None, description="The name of the team.")
    description: Optional[str] = Field(None, description="[Opt In](/docs/inputoutput-options). The description of the team.")
    html_description: Optional[str] = Field(None, description="[Opt In](/docs/inputoutput-options). The description of the team with formatting as HTML.")
    organization: Optional['WorkspaceCompact'] = None
    visibility: Optional[str] = Field(None, description="The visibility of the team to users in the same organization")
    edit_team_name_or_description_access_level: Optional[str] = Field(None, description="Controls who can edit team name and description")
    edit_team_visibility_or_trash_team_access_level: Optional[str] = Field(None, description="Controls who can edit team visibility and trash teams")
    member_invite_management_access_level: Optional[str] = Field(None, description="Controls who can accept or deny member invites for a given team")
    guest_invite_management_access_level: Optional[str] = Field(None, description="Controls who can accept or deny guest invites for a given team")
    join_request_management_access_level: Optional[str] = Field(None, description="Controls who can accept or deny join team requests for a Membership by Request team. This field can only be updated when the team's `visibility` field is `request_to_join`.")
    team_member_removal_access_level: Optional[str] = Field(None, description="Controls who can remove team members")
    team_content_management_access_level: Optional[str] = Field(None, description="Controls who can create and share content with the team")
    endorsed: Optional[bool] = Field(None, description="Whether the team has been endorsed")
    custom_field_settings: Optional[List['CustomFieldCompact']] = Field(None, description="Array of Custom Field Settings applied to the team.")

    class Config:
        from_attributes = True