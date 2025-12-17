"""Pydantic schema for Attachment Response"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class AttachmentResponse(BaseModel):
    """Attachment response schema"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.", example='12345')
    resource_type: Optional[str] = Field(description="The base type of this resource.", example='attachment')
    name: Optional[str] = Field(description="The name of the file.", example='Screenshot.png')
    resource_subtype: Optional[str] = Field(description="The service hosting the attachment. Valid values are `asana`, `dropbox`, `gdrive`, `onedrive`, `box`, `vimeo`, and `external`.", example='dropbox')
    created_at: Optional[datetime] = Field(description="The time at which this resource was created.", example='2012-02-22T02:06:58.147Z')
    download_url: Optional[str] = Field(description="The URL containing the content of the attachment. *Note:* May be null if the attachment is hosted by [Box](https://www.box.com/) and will be null if the attachment is a Video Message hosted by [Vimeo](https://vimeo.com/). If present, this URL may only be valid for two minutes from the time of retrieval. You should avoid persisting this URL somewhere and just refresh it on demand to ensure you do not keep stale URLs.", example='https://s3.amazonaws.com/assets/123/Screenshot.png')
    permanent_url: Optional[str] = Field(description="A stable URL for accessing the attachment through the Asana web application. This URL redirects to the file download location (e.g., an S3 link) if the user is authenticated and authorized to view the parent object (e.g., a task). Unauthorized users will receive a `403 Forbidden` response. This link is persistent and does not expire, but requires an active session to resolve.", example='https://app.asana.com/app/asana/-/get_asset?asset_id=1234567890')
    host: Optional[str] = Field(description="The service hosting the attachment. Valid values are `asana`, `dropbox`, `gdrive`, `onedrive`, `box`, `vimeo`, and `external`.", example='dropbox')
    parent: Optional['TaskCompact'] = None
    size: Optional[int] = Field(description="The size of the attachment in bytes. Only present when the `resource_subtype` is `asana`.", example=12345)
    view_url: Optional[str] = Field(description="The URL where the attachment can be viewed, which may be friendlier to users in a browser than just directing them to a raw file. May be null if no view URL exists for the service.", example='https://www.dropbox.com/s/123/Screenshot.png')
    connected_to_app: Optional[bool] = Field(description="Whether the attachment is connected to the app making the request for the purposes of showing an app components widget. Only present when the `resource_subtype` is `external` or `gdrive`.")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gid": "12345",
                "resource_type": "attachment",
                "name": "Example Name"
            }
        }

"""Pydantic schema for Attachment Compact (nested)"""
from pydantic import BaseModel, Field
from typing import Optional


class AttachmentCompact(BaseModel):
    """Attachment compact schema for nested responses"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.")
    resource_type: Optional[str] = Field(description="The base type of this resource.")
    name: Optional[str] = Field(description="The name of the file.")

    class Config:
        from_attributes = True

"""Pydantic schema for Attachment Create Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class AttachmentCreate(BaseModel):
    """Attachment create request schema"""

    resource_subtype: Optional[str] = Field(None, description="The service hosting the attachment. Valid values are `asana`, `dropbox`, `gdrive`, `onedrive`, `box`, `vimeo`, and `external`.")
    parent: Optional['TaskCompact'] = None

    class Config:
        from_attributes = True

"""Pydantic schema for Attachment Update Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class AttachmentUpdate(BaseModel):
    """Attachment update request schema"""

    resource_subtype: Optional[str] = Field(None, description="The service hosting the attachment. Valid values are `asana`, `dropbox`, `gdrive`, `onedrive`, `box`, `vimeo`, and `external`.")
    parent: Optional['TaskCompact'] = None

    class Config:
        from_attributes = True