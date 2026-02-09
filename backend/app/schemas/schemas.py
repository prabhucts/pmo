"""
Pydantic schemas for request/response models
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


# Enums
class InsightType(str, Enum):
    PROJECT_OVERRUN = "project_overrun"
    UNDER_UTILIZATION = "under_utilization"
    PROJECT_ENDED_ALLOCATION_EXISTS = "project_ended_allocation_exists"
    TEAM_HOUR_TRACKING = "team_hour_tracking"
    FORECAST_ALERT = "forecast_alert"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class RuleType(str, Enum):
    CONVERSION = "conversion"
    VALIDATION = "validation"
    ALERT = "alert"
    CALCULATION = "calculation"


# Base schemas
class ProjectBase(BaseModel):
    itpr_code: str
    name: str
    theme: Optional[str] = None
    owner: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "Active"


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserStoryBase(BaseModel):
    formatted_id: str
    name: str
    owner: Optional[str] = None
    team: Optional[str] = None
    release: Optional[str] = None
    iteration: Optional[str] = None
    plan_estimate: float = 0.0
    state: Optional[str] = None


class UserStoryCreate(UserStoryBase):
    feature_id: Optional[int] = None


class UserStory(UserStoryBase):
    id: int
    feature_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TeamMemberBase(BaseModel):
    name: str
    email: EmailStr
    network_id: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    allocation_percentage: float = 100.0
    is_active: bool = True


class TeamMemberCreate(TeamMemberBase):
    team_id: Optional[int] = None


class TeamMember(TeamMemberBase):
    id: int
    team_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SprintBase(BaseModel):
    name: str
    release: str
    start_date: date
    end_date: date
    sprint_number: Optional[int] = None
    is_active: bool = True


class SprintCreate(SprintBase):
    pass


class Sprint(SprintBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class BusinessRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    rule_type: RuleType
    parameters: Dict[str, Any] = {}
    is_active: bool = True
    priority: int = 0


class BusinessRuleCreate(BusinessRuleBase):
    pass


class BusinessRule(BusinessRuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class InsightBase(BaseModel):
    insight_type: InsightType
    title: str
    description: Optional[str] = None
    severity: Severity = Severity.INFO
    project_id: Optional[int] = None
    team_id: Optional[int] = None
    data: Dict[str, Any] = {}


class InsightCreate(InsightBase):
    pass


class Insight(InsightBase):
    id: int
    is_resolved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    session_id: str


class FileUploadResponse(BaseModel):
    filename: str
    file_type: str
    rows_processed: int
    status: str
    message: str


class DashboardSummary(BaseModel):
    total_projects: int
    active_projects: int
    total_sprints: int
    active_sprint: Optional[str] = None
    total_teams: int
    total_team_members: int
    total_user_stories: int
    total_story_points: float
    insights_count: Dict[str, int] = {}


class ProjectOverrunInsight(BaseModel):
    project: Project
    planned_hours: float
    actual_hours: float
    overrun_hours: float
    overrun_percentage: float


class TeamUtilizationInsight(BaseModel):
    team_name: str
    allocated_hours: float
    available_hours: float
    utilization_percentage: float
    team_members: List[TeamMember]


class ForecastData(BaseModel):
    project: Project
    remaining_story_points: float
    team_velocity: float
    estimated_completion_date: Optional[date] = None
    confidence_level: str
    risks: List[str] = []
