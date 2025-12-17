"""Pydantic schema for User Response"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class UserResponse(BaseModel):
    """User response schema"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.", example='12345')
    resource_type: Optional[str] = Field(description="The base type of this resource.", example='user')
    name: Optional[str] = Field(description="*Read-only except when same user as requester*. The user's name.", example='Greg Sanchez')
    email: Optional[str] = Field(description="The user's email address.", example='gsanchez@example.com')
    photo: Optional[dict] = Field(description="A map of the user's profile photo in various sizes, or null if no photo is set. Sizes provided are 21, 27, 36, 60, 128, and 1024. All images are in PNG format, except for 1024 (which is in JPEG format).", example={'image_21x21': 'https://...', 'image_27x27': 'https://...', 'image_36x36': 'https://...', 'image_60x60': 'https://...', 'image_128x128': 'https://...', 'image_1024x1024': 'https://...'})
    workspaces: Optional[List['WorkspaceCompact']] = Field(description="Workspaces and organizations this user may access. Note\: The API will only return workspaces and organizations that also contain the authenticated user.")
    custom_fields: Optional[List['CustomFieldCompact']] = Field(description="Array of Custom Fields.")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gid": "12345",
                "resource_type": "user",
                "name": "Example Name"
            }
        }

"""Pydantic schema for User Compact (nested)"""
from pydantic import BaseModel, Field
from typing import Optional


class UserCompact(BaseModel):
    """User compact schema for nested responses"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.")
    resource_type: Optional[str] = Field(description="The base type of this resource.")
    name: str = Field(description="*Read-only except when same user as requester*. The user's name.")

    class Config:
        from_attributes = True

"""Pydantic schema for User Create Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class UserCreate(BaseModel):
    """User create request schema"""

    name: Optional[str] = Field(None, description="*Read-only except when same user as requester*. The user's name.")
    custom_fields: Optional[List['CustomFieldCompact']] = Field(None, description="Array of Custom Fields.")

    class Config:
        from_attributes = True

"""Pydantic schema for User Update Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class UserUpdate(BaseModel):
    """User update request schema"""

    name: Optional[str] = Field(None, max_length=256, description="*Read-only except when same user as requester*. The user's name.")
    custom_fields: Optional[List['CustomFieldCompact']] = Field(None, description="Array of Custom Fields.")

    class Config:
        from_attributes = True