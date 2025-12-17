"""Pydantic schema for Section Response"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class SectionResponse(BaseModel):
    """Section response schema"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.", example='12345')
    resource_type: Optional[str] = Field(description="The base type of this resource.", example='section')
    name: Optional[str] = Field(description="The name of the section (i.e. the text displayed as the section header).", example='Next Actions')
    created_at: Optional[datetime] = Field(description="The time at which this resource was created.", example='2012-02-22T02:06:58.147Z')
    project: Optional[str] = None
    projects: Optional[List['ProjectCompact']] = Field(description="*Deprecated - please use project instead*")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gid": "12345",
                "resource_type": "section",
                "name": "Example Name"
            }
        }

"""Pydantic schema for Section Compact (nested)"""
from pydantic import BaseModel, Field
from typing import Optional


class SectionCompact(BaseModel):
    """Section compact schema for nested responses"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.")
    resource_type: Optional[str] = Field(description="The base type of this resource.")
    name: str = Field(description="The name of the section (i.e. the text displayed as the section header).")

    class Config:
        from_attributes = True

"""Pydantic schema for Section Create Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class SectionCreate(BaseModel):
    """Section create request schema"""

    name: Optional[str] = Field(None, description="The name of the section (i.e. the text displayed as the section header).")
    project: Optional[str] = None

    class Config:
        from_attributes = True

"""Pydantic schema for Section Update Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class SectionUpdate(BaseModel):
    """Section update request schema"""

    name: Optional[str] = Field(None, description="The name of the section (i.e. the text displayed as the section header).")
    project: Optional[str] = None

    class Config:
        from_attributes = True