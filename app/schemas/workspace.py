"""Pydantic schema for Workspace Response"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class WorkspaceResponse(BaseModel):
    """Workspace response schema"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.", example='12345')
    resource_type: Optional[str] = Field(description="The base type of this resource.", example='workspace')
    name: Optional[str] = Field(description="The name of the workspace.", example='My Company Workspace')
    email_domains: Optional[List[str]] = Field(description="The email domains that are associated with this workspace.", example=['asana.com'])
    is_organization: Optional[bool] = Field(description="Whether the workspace is an *organization*.", example=False)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gid": "12345",
                "resource_type": "workspace",
                "name": "Example Name"
            }
        }

"""Pydantic schema for Workspace Compact (nested)"""
from pydantic import BaseModel, Field
from typing import Optional


class WorkspaceCompact(BaseModel):
    """Workspace compact schema for nested responses"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.")
    resource_type: Optional[str] = Field(description="The base type of this resource.")
    name: str = Field(description="The name of the workspace.")

    class Config:
        from_attributes = True

"""Pydantic schema for Workspace Create Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class WorkspaceCreate(BaseModel):
    """Workspace create request schema"""

    name: Optional[str] = Field(None, max_length=256, description="The name of the workspace.")
    email_domains: Optional[List[str]] = Field(None, description="The email domains that are associated with this workspace.")
    is_organization: Optional[bool] = Field(None, description="Whether the workspace is an *organization*.")

    class Config:
        from_attributes = True

"""Pydantic schema for Workspace Update Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class WorkspaceUpdate(BaseModel):
    """Workspace update request schema"""

    name: Optional[str] = Field(None, max_length=256, description="The name of the workspace.")
    email_domains: Optional[List[str]] = Field(None, description="The email domains that are associated with this workspace.")
    is_organization: Optional[bool] = Field(None, description="Whether the workspace is an *organization*.")

    class Config:
        from_attributes = True