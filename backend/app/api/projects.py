"""
Projects API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models import Project, Epic, Feature, UserStory
from app.schemas.schemas import Project as ProjectSchema, ProjectCreate

router = APIRouter()


@router.get("/", response_model=List[ProjectSchema])
async def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all projects"""
    projects = db.query(Project).offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectSchema)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/summary")
async def get_project_summary(project_id: int, db: Session = Depends(get_db)):
    """Get project summary with statistics"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Count epics, features, user stories
    epics = db.query(Epic).filter(Epic.project_id == project_id).all()
    epic_ids = [e.id for e in epics]
    
    features = db.query(Feature).filter(Feature.epic_id.in_(epic_ids)).all() if epic_ids else []
    feature_ids = [f.id for f in features]
    
    user_stories = db.query(UserStory).filter(UserStory.feature_id.in_(feature_ids)).all() if feature_ids else []
    
    total_sp = sum(us.plan_estimate for us in user_stories)
    completed_sp = sum(us.plan_estimate for us in user_stories if us.state in ["Completed", "Accepted"])
    
    return {
        "project": {
            "id": project.id,
            "itpr_code": project.itpr_code,
            "name": project.name,
            "status": project.status
        },
        "epics_count": len(epics),
        "features_count": len(features),
        "user_stories_count": len(user_stories),
        "total_story_points": total_sp,
        "completed_story_points": completed_sp,
        "completion_percentage": (completed_sp / total_sp * 100) if total_sp > 0 else 0
    }


@router.post("/", response_model=ProjectSchema)
async def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project
