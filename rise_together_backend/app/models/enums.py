import enum


class UserRole(str, enum.Enum):
    learner = "learner"
    mentor = "mentor"
    admin = "admin"


class ModuleType(str, enum.Enum):
    path = "path"
    module = "module"
    lesson = "lesson"
    assignment = "assignment"
    project = "project"
    milestone = "milestone"


class UserModuleStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"


class LinkType(str, enum.Enum):
    github = "github"
    portfolio = "portfolio"
    submission = "submission"
    projects = "projects"
    resources = "resources"
    other = "other"


class LinkReviewStatus(str, enum.Enum):
    pending = "pending"
    reviewed = "reviewed"

class SubLinkType(str, enum.Enum):
    """
    Optional constraint on a submission slot.
    Only relevant when LinkType == submission.
    None means any URL is acceptable.
    """
    github = "github"
    youtube = "youtube"
    google_drive = "google_drive"
    figma = "figma"
    other = "other"