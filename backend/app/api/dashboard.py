"""
Dashboard API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models import Project, Team, TeamMember, UserStory, Sprint, Insight
from app.schemas.schemas import DashboardSummary

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary statistics"""
    
    # Count totals
    total_projects = db.query(Project).count()
    active_projects = db.query(Project).filter(Project.status == "Active").count()
    total_sprints = db.query(Sprint).count()
    total_teams = db.query(Team).count()
    total_team_members = db.query(TeamMember).filter(TeamMember.is_active == True).count()
    total_user_stories = db.query(UserStory).count()
    total_story_points = db.query(func.sum(UserStory.plan_estimate)).scalar() or 0.0
    
    # Get active sprint
    active_sprint = db.query(Sprint).filter(Sprint.is_active == True).first()
    active_sprint_name = active_sprint.name if active_sprint else None
    
    # Count insights by type
    insights_by_type = db.query(
        Insight.insight_type, 
        func.count(Insight.id)
    ).filter(
        Insight.is_resolved == False
    ).group_by(
        Insight.insight_type
    ).all()
    
    insights_count = {insight_type: count for insight_type, count in insights_by_type}
    
    return DashboardSummary(
        total_projects=total_projects,
        active_projects=active_projects,
        total_sprints=total_sprints,
        active_sprint=active_sprint_name,
        total_teams=total_teams,
        total_team_members=total_team_members,
        total_user_stories=total_user_stories,
        total_story_points=total_story_points,
        insights_count=insights_count
    )
