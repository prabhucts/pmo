"""
Database models for PMO application
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Project(Base):
    """Project/ITPR model"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    itpr_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    theme = Column(String)
    owner = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default="Active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    epics = relationship("Epic", back_populates="project")
    allocations = relationship("TeamAllocation", back_populates="project")


class Epic(Base):
    """Epic model"""
    __tablename__ = "epics"
    
    id = Column(Integer, primary_key=True, index=True)
    formatted_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    state = Column(String)
    percent_done_by_story_plan = Column(Float, default=0.0)
    percent_done_by_story_count = Column(Float, default=0.0)
    owner = Column(String)
    tags = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="epics")
    features = relationship("Feature", back_populates="epic")


class Feature(Base):
    """Feature model"""
    __tablename__ = "features"
    
    id = Column(Integer, primary_key=True, index=True)
    formatted_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    epic_id = Column(Integer, ForeignKey("epics.id"))
    state = Column(String)
    owner = Column(String)
    release = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    epic = relationship("Epic", back_populates="features")
    user_stories = relationship("UserStory", back_populates="feature")


class UserStory(Base):
    """User Story model"""
    __tablename__ = "user_stories"
    
    id = Column(Integer, primary_key=True, index=True)
    formatted_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    feature_id = Column(Integer, ForeignKey("features.id"))
    owner = Column(String)
    team = Column(String, index=True)
    release = Column(String)
    iteration = Column(String, index=True)  # Sprint
    plan_estimate = Column(Float, default=0.0)  # Story points
    state = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    feature = relationship("Feature", back_populates="user_stories")
    defects = relationship("Defect", back_populates="user_story")


class Defect(Base):
    """Defect model"""
    __tablename__ = "defects"
    
    id = Column(Integer, primary_key=True, index=True)
    formatted_id = Column(String, unique=True, index=True)
    name = Column(String)
    user_story_id = Column(Integer, ForeignKey("user_stories.id"), nullable=True)
    feature_formatted_id = Column(String, nullable=True)  # Direct feature reference
    team = Column(String, index=True)
    iteration = Column(String)
    plan_estimate = Column(Float, default=0.0)
    state = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_story = relationship("UserStory", back_populates="defects")


class Team(Base):
    """Team model"""
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    members = relationship("TeamMember", back_populates="team")
    allocations = relationship("TeamAllocation", back_populates="team")


class TeamMember(Base):
    """Team Member model"""
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    network_id = Column(String)
    team_id = Column(Integer, ForeignKey("teams.id"))
    role = Column(String)  # Engineering Lead, Product, etc.
    location = Column(String)  # Onsite, Offshore
    allocation_percentage = Column(Float, default=100.0)  # % allocation to rally work
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="members")
    time_entries = relationship("TimeEntry", back_populates="team_member")


class TeamAllocation(Base):
    """Team allocation to projects (from Clarity)"""
    __tablename__ = "team_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    team_member_id = Column(Integer, ForeignKey("team_members.id"))
    week_start_date = Column(Date, nullable=False, index=True)
    allocated_hours = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="allocations")
    project = relationship("Project", back_populates="allocations")
    team_member = relationship("TeamMember")


class TimeEntry(Base):
    """Actual time entries from Clarity"""
    __tablename__ = "time_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    team_member_id = Column(Integer, ForeignKey("team_members.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    week_start_date = Column(Date, nullable=False, index=True)
    actual_hours = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    team_member = relationship("TeamMember", back_populates="time_entries")
    project = relationship("Project")


class Sprint(Base):
    """Sprint/Iteration model"""
    __tablename__ = "sprints"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # e.g., "2026.S1"
    release = Column(String, nullable=False)  # e.g., "2026.Jan"
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    sprint_number = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessRule(Base):
    """Configurable business rules"""
    __tablename__ = "business_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    rule_type = Column(String, nullable=False)  # conversion, validation, alert, etc.
    parameters = Column(JSON)  # Store rule parameters as JSON
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Insight(Base):
    """Generated insights and alerts"""
    __tablename__ = "insights"
    
    id = Column(Integer, primary_key=True, index=True)
    insight_type = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    severity = Column(String, default="info")  # info, warning, critical
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    data = Column(JSON)  # Additional insight data
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project")
    team = relationship("Team")


class ChatHistory(Base):
    """Chat conversation history"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    intent = Column(String)
    context = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
