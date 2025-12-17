"""Pydantic schema for Tag Response"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class TagResponse(BaseModel):
    """Tag response schema"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.", example='12345')
    resource_type: Optional[str] = Field(description="The base type of this resource.", example='tag')
    name: Optional[str] = Field(description="Name of the tag. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.", example='Stuff to buy')
    color: Optional[str] = Field(description="Color of the tag.", example='light-green')
    notes: Optional[str] = Field(description="Free-form textual information associated with the tag (i.e. its description).", example='Mittens really likes the stuff from Humboldt.')
    created_at: Optional[datetime] = Field(description="The time at which this resource was created.", example='2012-02-22T02:06:58.147Z')
    followers: Optional[List['UserCompact']] = Field(description="Array of users following this tag.")
    workspace: Optional[str] = None
    permalink_url: Optional[str] = Field(description="A url that points directly to the object within Asana.", example='https://app.asana.com/0/resource/123456789/list')

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gid": "12345",
                "resource_type": "tag",
                "name": "Example Name"
            }
        }

"""Pydantic schema for Tag Compact (nested)"""
from pydantic import BaseModel, Field
from typing import Optional


class TagCompact(BaseModel):
    """Tag compact schema for nested responses"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.")
    resource_type: Optional[str] = Field(description="The base type of this resource.")
    name: str = Field(description="Name of the tag. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")

    class Config:
        from_attributes = True

"""Pydantic schema for Tag Create Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class TagCreate(BaseModel):
    """Tag create request schema"""

    name: Optional[str] = Field(None, description="Name of the tag. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")
    color: Optional[str] = Field(None, description="Color of the tag.")
    notes: Optional[str] = Field(None, description="Free-form textual information associated with the tag (i.e. its description).")
    workspace: Optional[str] = None

    class Config:
        from_attributes = True

"""Pydantic schema for Tag Update Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class TagUpdate(BaseModel):
    """Tag update request schema"""

    name: Optional[str] = Field(None, description="Name of the tag. This is generally a short sentence fragment that fits on a line in the UI for maximum readability. However, it can be longer.")
    color: Optional[str] = Field(None, description="Color of the tag.")
    notes: Optional[str] = Field(None, description="Free-form textual information associated with the tag (i.e. its description).")
    workspace: Optional[str] = None

    class Config:
        from_attributes = True