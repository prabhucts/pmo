"""
Business Rules API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models import BusinessRule
from app.schemas.schemas import BusinessRule as RuleSchema, BusinessRuleCreate

router = APIRouter()


@router.get("/", response_model=List[RuleSchema])
async def get_rules(
    rule_type: str = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all business rules"""
    query = db.query(BusinessRule)
    
    if rule_type:
        query = query.filter(BusinessRule.rule_type == rule_type)
    
    if active_only:
        query = query.filter(BusinessRule.is_active == True)
    
    rules = query.order_by(BusinessRule.priority.desc()).all()
    return rules


@router.post("/", response_model=RuleSchema)
async def create_rule(rule: BusinessRuleCreate, db: Session = Depends(get_db)):
    """Create a new business rule"""
    db_rule = BusinessRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.put("/{rule_id}", response_model=RuleSchema)
async def update_rule(rule_id: int, rule: BusinessRuleCreate, db: Session = Depends(get_db)):
    """Update a business rule"""
    db_rule = db.query(BusinessRule).filter(BusinessRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    for key, value in rule.dict().items():
        setattr(db_rule, key, value)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.delete("/{rule_id}")
async def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a business rule"""
    db_rule = db.query(BusinessRule).filter(BusinessRule.id == rule_id).first()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(db_rule)
    db.commit()
    return {"message": "Rule deleted"}
