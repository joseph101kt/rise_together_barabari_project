# Single import point for all schemas.
# Usage in routers:
#   from app.schemas import RegisterRequest, TokenResponse, ModuleCardResponse

from app.schemas.auth import (  # noqa: F401
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.modules import (  # noqa: F401
    ModuleResponse,
)
from app.schemas.progress import (  # noqa: F401
    LinkProgressRequest,
    LinkProgressResponse,
    ModuleProgressRequest,
    ModuleProgressResponse,
    SubmissionLinkResponse,
    SubmissionModuleResponse,
    UserSubmissionsResponse,
)
from app.schemas.shared import (  # noqa: F401
    LinkResponse,
    ModuleLinkResponse,
    ProfileLinkResponse,
    SkillResponse,
)
from app.schemas.users import (  # noqa: F401
    EducationRequest,
    EducationResponse,
    ExperienceRequest,
    ExperienceResponse,
    FullProfileResponse,
    ProfileLinkRequest,
    ProfileResponse,
    ProfileUpdateData,
    ProfileUpdateRequest,
    PublicProfileResponse,
    PublicUserResponse,
    UserResponse,
)