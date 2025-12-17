"""Pydantic Schemas for Request/Response Validation"""

from app.schemas.workspace import (
    WorkspaceResponse,
    WorkspaceCompact,
    WorkspaceCreate,
    WorkspaceUpdate,
)

from app.schemas.project import (
    ProjectResponse,
    ProjectCompact,
    ProjectCreate,
    ProjectUpdate,
)

from app.schemas.task import (
    TaskResponse,
    TaskCompact,
    TaskCreate,
    TaskUpdate,
)

from app.schemas.user import (
    UserResponse,
    UserCompact,
    UserCreate,
    UserUpdate,
)

from app.schemas.team import (
    TeamResponse,
    TeamCompact,
    TeamCreate,
    TeamUpdate,
)

from app.schemas.section import (
    SectionResponse,
    SectionCompact,
    SectionCreate,
    SectionUpdate,
)

from app.schemas.attachment import (
    AttachmentResponse,
    AttachmentCompact,
    AttachmentCreate,
    AttachmentUpdate,
)

from app.schemas.story import (
    StoryResponse,
    StoryCompact,
    StoryCreate,
    StoryUpdate,
)

from app.schemas.tag import (
    TagResponse,
    TagCompact,
    TagCreate,
    TagUpdate,
)

from app.schemas.webhook import (
    WebhookResponse,
    WebhookCompact,
    WebhookCreate,
    WebhookUpdate,
)

from app.schemas.custom_field import (
    CustomFieldResponse,
    CustomFieldCompact,
    CustomFieldCreate,
    CustomFieldUpdate,
)

# Export all schemas
__all__ = [
    "WorkspaceResponse",
    "WorkspaceCompact",
    "WorkspaceCreate",
    "WorkspaceUpdate",
    "ProjectResponse",
    "ProjectCompact",
    "ProjectCreate",
    "ProjectUpdate",
    "TaskResponse",
    "TaskCompact",
    "TaskCreate",
    "TaskUpdate",
    "UserResponse",
    "UserCompact",
    "UserCreate",
    "UserUpdate",
    "TeamResponse",
    "TeamCompact",
    "TeamCreate",
    "TeamUpdate",
    "SectionResponse",
    "SectionCompact",
    "SectionCreate",
    "SectionUpdate",
    "AttachmentResponse",
    "AttachmentCompact",
    "AttachmentCreate",
    "AttachmentUpdate",
    "StoryResponse",
    "StoryCompact",
    "StoryCreate",
    "StoryUpdate",
    "TagResponse",
    "TagCompact",
    "TagCreate",
    "TagUpdate",
    "WebhookResponse",
    "WebhookCompact",
    "WebhookCreate",
    "WebhookUpdate",
    "CustomFieldResponse",
    "CustomFieldCompact",
    "CustomFieldCreate",
    "CustomFieldUpdate",
]