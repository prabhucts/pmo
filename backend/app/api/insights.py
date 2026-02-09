"""
Insights API endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date

from app.db.database import get_db
from app.db.models import Insight, Project, Team
from app.schemas.schemas import Insight as InsightSchema, InsightCreate
from app.services.business_rules import BusinessRulesEngine

router = APIRouter()


@router.get("/", response_model=List[InsightSchema])
async def get_insights(
    insight_type: Optional[str] = None,
    resolved: Optional[bool] = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all insights"""
    query = db.query(Insight)
    
    if insight_type:
        query = query.filter(Insight.insight_type == insight_type)
    
    if resolved is not None:
        query = query.filter(Insight.is_resolved == resolved)
    
    insights = query.offset(skip).limit(limit).all()
    return insights


@router.get("/generate")
async def generate_insights(db: Session = Depends(get_db)):
    """Generate fresh insights"""
    rules_engine = BusinessRulesEngine(db)
    generated_insights = []
    
    # Generate project overrun insights
    projects = db.query(Project).filter(Project.status == "Active").all()
    for project in projects:
        overrun_data = rules_engine.detect_project_overruns(project.id)
        if overrun_data.get("is_overrun"):
            insight = Insight(
                insight_type="project_overrun",
                title=f"Project Overrun: {overrun_data['project_name']}",
                description=f"Project has overrun by {overrun_data['overrun_hours']:.1f} hours ({overrun_data['overrun_percentage']:.1f}%)",
                severity="warning" if overrun_data['overrun_percentage'] < 20 else "critical",
                project_id=project.id,
                data=overrun_data
            )
            db.add(insight)
            generated_insights.append("project_overrun")
    
    # Generate under-utilization insights
    teams = db.query(Team).all()
    current_week = date.today()
    
    for team in teams:
        util_data = rules_engine.detect_under_utilization(team.id, current_week)
        if util_data.get("is_under_utilized"):
            insight = Insight(
                insight_type="under_utilization",
                title=f"Team Under-Utilized: {util_data['team_name']}",
                description=f"Team is only {util_data['utilization_percentage']:.1f}% utilized",
                severity="info",
                team_id=team.id,
                data=util_data
            )
            db.add(insight)
            generated_insights.append("under_utilization")
    
    # Generate forecast alerts
    for project in projects:
        forecast = rules_engine.forecast_project_completion(project.id)
        if forecast.get("risks"):
            insight = Insight(
                insight_type="forecast_alert",
                title=f"Forecast Risks: {forecast['project_name']}",
                description=f"Project has {len(forecast['risks'])} identified risks",
                severity="warning",
                project_id=project.id,
                data=forecast
            )
            db.add(insight)
            generated_insights.append("forecast_alert")
    
    db.commit()
    
    return {
        "message": f"Generated {len(generated_insights)} insights",
        "insights_by_type": {
            insight_type: generated_insights.count(insight_type)
            for insight_type in set(generated_insights)
        }
    }


@router.patch("/{insight_id}/resolve")
async def resolve_insight(insight_id: int, db: Session = Depends(get_db)):
    """Mark an insight as resolved"""
    insight = db.query(Insight).filter(Insight.id == insight_id).first()
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    insight.is_resolved = True
    db.commit()
    
    return {"message": "Insight resolved", "insight_id": insight_id}
