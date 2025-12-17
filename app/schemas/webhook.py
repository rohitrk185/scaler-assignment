"""Pydantic schema for Webhook Response"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class WebhookResponse(BaseModel):
    """Webhook response schema"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.", example='12345')
    resource_type: Optional[str] = Field(description="The base type of this resource.", example='webhook')
    active: Optional[bool] = Field(description="If true, the webhook will send events - if false it is considered inactive and will not generate events.", example=False)
    resource: Optional[str] = None
    target: Optional[str] = Field(description="The URL to receive the HTTP POST.", example='https://example.com/receive-webhook/7654')
    created_at: Optional[datetime] = Field(description="The time at which this resource was created.", example='2012-02-22T02:06:58.147Z')
    last_failure_at: Optional[datetime] = Field(description="The timestamp when the webhook last received an error when sending an event to the target.", example='2012-02-22T02:06:58.147Z')
    last_failure_content: Optional[str] = Field(description="The contents of the last error response sent to the webhook when attempting to deliver events to the target.", example='500 Server Error\\n\\nCould not complete the request')
    last_success_at: Optional[datetime] = Field(description="The timestamp when the webhook last successfully sent an event to the target.", example='2012-02-22T02:06:58.147Z')
    delivery_retry_count: Optional[int] = Field(description="The number of times the webhook has retried delivery of events to the target (resets after a successful attempt).", example=3)
    next_attempt_after: Optional[datetime] = Field(description="The timestamp after which the webhook will next attempt to deliver an event to the target.", example='2012-02-22T02:06:58.147Z')
    failure_deletion_timestamp: Optional[datetime] = Field(description="The timestamp when the webhook will be deleted if there is no successful attempt to deliver events to the target", example='2012-02-22T02:06:58.147Z')
    filters: Optional[List[str]] = Field(description="Whitelist of filters to apply to events from this webhook. If a webhook event passes any of the filters the event will be delivered; otherwise no event will be sent to the receiving server.")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "gid": "12345",
                "resource_type": "webhook",
                "name": "Example Name"
            }
        }

"""Pydantic schema for Webhook Compact (nested)"""
from pydantic import BaseModel, Field
from typing import Optional


class WebhookCompact(BaseModel):
    """Webhook compact schema for nested responses"""

    gid: Optional[str] = Field(description="Globally unique identifier of the resource, as a string.")
    resource_type: Optional[str] = Field(description="The base type of this resource.")

    class Config:
        from_attributes = True

"""Pydantic schema for Webhook Create Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class WebhookCreate(BaseModel):
    """Webhook create request schema"""

    resource: Optional[str] = None
    target: Optional[str] = Field(None, description="The URL to receive the HTTP POST.")
    filters: Optional[List[str]] = Field(None, description="Whitelist of filters to apply to events from this webhook. If a webhook event passes any of the filters the event will be delivered; otherwise no event will be sent to the receiving server.")

    class Config:
        from_attributes = True

"""Pydantic schema for Webhook Update Request"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class WebhookUpdate(BaseModel):
    """Webhook update request schema"""

    resource: Optional[str] = None
    filters: Optional[List[str]] = Field(None, description="Whitelist of filters to apply to events from this webhook. If a webhook event passes any of the filters the event will be delivered; otherwise no event will be sent to the receiving server.")

    class Config:
        from_attributes = True