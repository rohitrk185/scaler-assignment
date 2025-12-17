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

# Rebuild models with forward references
# This is needed for forward references like 'UserCompact', 'ProjectCompact', etc.
# Rebuild in order: base types first, then dependent types
WorkspaceCompact.model_rebuild()
UserCompact.model_rebuild()
ProjectCompact.model_rebuild()
TeamCompact.model_rebuild()
SectionCompact.model_rebuild()
TagCompact.model_rebuild()
TaskCompact.model_rebuild()
StoryCompact.model_rebuild()
CustomFieldCompact.model_rebuild()
AttachmentCompact.model_rebuild()

# Now rebuild response models that depend on compact types
SectionResponse.model_rebuild()
TagResponse.model_rebuild()
StoryResponse.model_rebuild()
TaskResponse.model_rebuild()
TaskCreate.model_rebuild()
TaskUpdate.model_rebuild()
ProjectResponse.model_rebuild()
ProjectCreate.model_rebuild()
ProjectUpdate.model_rebuild()
CustomFieldResponse.model_rebuild()
CustomFieldCreate.model_rebuild()
CustomFieldUpdate.model_rebuild()
TeamResponse.model_rebuild()
TeamCreate.model_rebuild()
TeamUpdate.model_rebuild()
AttachmentResponse.model_rebuild()
AttachmentCreate.model_rebuild()
AttachmentUpdate.model_rebuild()
StoryResponse.model_rebuild()
StoryCreate.model_rebuild()
StoryUpdate.model_rebuild()