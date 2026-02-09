"""
Business Rules Engine - Extracted from VBA logic
"""
from typing import Dict, List, Optional, Any
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import pandas as pd

from app.db.models import (
    Project, UserStory, Feature, Epic, TeamMember, 
    Team, TeamAllocation, TimeEntry, Sprint, BusinessRule
)
from app.core.config import settings


class BusinessRulesEngine:
    """
    Business rules engine implementing logic from VBA modules
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load active business rules from database"""
        rules_db = self.db.query(BusinessRule).filter(
            BusinessRule.is_active == True
        ).all()
        
        rules = {}
        for rule in rules_db:
            rules[rule.name] = rule.parameters
        
        # Set defaults if not in database
        if "story_point_hours" not in rules:
            rules["story_point_hours"] = {"value": settings.DEFAULT_STORY_POINT_HOURS}
        if "sprint_weeks" not in rules:
            rules["sprint_weeks"] = {"value": settings.DEFAULT_SPRINT_WEEKS}
        if "working_days_per_week" not in rules:
            rules["working_days_per_week"] = {"value": settings.DEFAULT_WORKING_DAYS_PER_WEEK}
        if "hours_per_day" not in rules:
            rules["hours_per_day"] = {"value": settings.DEFAULT_HOURS_PER_DAY}
        
        return rules
    
    def get_story_point_hours(self, team_name: Optional[str] = None) -> float:
        """
        Get story point to hours conversion
        1 Story Point = 13 hours (default, configurable per team)
        """
        if team_name and f"sp_hours_{team_name}" in self.rules:
            return self.rules[f"sp_hours_{team_name}"]["value"]
        return self.rules["story_point_hours"]["value"]
    
    def convert_story_points_to_hours(self, story_points: float, team_name: Optional[str] = None) -> float:
        """Convert story points to hours"""
        sp_hours = self.get_story_point_hours(team_name)
        return story_points * sp_hours
    
    def calculate_total_hours_for_feature(self, feature_id: int, team_name: str) -> Dict[str, float]:
        """
        Calculate total hours for a feature including defects
        Logic from Module1.vba lines 458-476
        """
        # Get user stories for this feature and team
        user_stories = self.db.query(UserStory).filter(
            and_(
                UserStory.feature_id == feature_id,
                UserStory.team == team_name
            )
        ).all()
        
        total_sp = sum(us.plan_estimate for us in user_stories)
        
        # Get defects associated with this feature
        # Logic from defectestimate function (lines 739-805)
        defect_sp = self._calculate_defect_estimate(feature_id, team_name)
        
        total_sp += defect_sp
        total_hours = self.convert_story_points_to_hours(total_sp, team_name)
        
        return {
            "total_story_points": total_sp,
            "total_hours": total_hours,
            "user_story_sp": total_sp - defect_sp,
            "defect_sp": defect_sp
        }
    
    def _calculate_defect_estimate(self, feature_id: int, team_name: str) -> float:
        """
        Calculate defect estimate for a feature
        Logic from defectestimate function (Module1.vba lines 739-805)
        """
        from app.db.models import Defect
        
        # Get feature formatted ID
        feature = self.db.query(Feature).filter(Feature.id == feature_id).first()
        if not feature:
            return 0.0
        
        # Get defects linked to this feature or its user stories
        defects = self.db.query(Defect).filter(
            and_(
                Defect.team == team_name,
                (
                    Defect.feature_formatted_id == feature.formatted_id
                )
            )
        ).all()
        
        total_defect_sp = sum(d.plan_estimate for d in defects)
        return total_defect_sp
    
    def calculate_hours_per_week(self, total_hours: float, team_name: str, weeks: Optional[int] = None) -> float:
        """
        Calculate hours per week based on total hours
        Logic from CalculateHours function (Module1.vba lines 717-737)
        """
        if weeks is None:
            weeks = self.rules["sprint_weeks"]["value"] * 5  # Default to PI weeks
        
        # Get team count
        team = self.db.query(Team).filter(Team.name == team_name).first()
        if not team:
            return 0.0
        
        team_count = self.db.query(TeamMember).filter(
            and_(
                TeamMember.team_id == team.id,
                TeamMember.is_active == True
            )
        ).count()
        
        if team_count == 0:
            return 0.0
        
        # Get rally allocation percentage for the team
        rally_allocation = self._get_team_rally_allocation(team_name)
        
        hours_per_week = (total_hours * rally_allocation) / weeks / team_count if weeks > 0 else 0
        return round(hours_per_week, 2)
    
    def _get_team_rally_allocation(self, team_name: str) -> float:
        """
        Get team rally allocation percentage (from Reference sheet logic)
        Logic from Module1.vba lines 374-377
        """
        team = self.db.query(Team).filter(Team.name == team_name).first()
        if not team:
            return 1.0
        
        members = self.db.query(TeamMember).filter(
            and_(
                TeamMember.team_id == team.id,
                TeamMember.is_active == True
            )
        ).all()
        
        if not members:
            return 1.0
        
        # Average allocation percentage across team
        total_allocation = sum(m.allocation_percentage for m in members)
        avg_allocation = total_allocation / len(members) / 100.0
        
        return avg_allocation
    
    def calculate_clarity_allocation(
        self, 
        itpr_code: str, 
        team_member_id: int,
        weeks: List[date]
    ) -> Dict[str, float]:
        """
        Calculate Clarity allocation for a team member on a project
        Logic from ClaritySheet function (Module1.vba lines 559-611)
        """
        project = self.db.query(Project).filter(Project.itpr_code == itpr_code).first()
        if not project:
            return {}
        
        team_member = self.db.query(TeamMember).filter(TeamMember.id == team_member_id).first()
        if not team_member:
            return {}
        
        # Get estimate from summary (all features for this project and team)
        estimate = self._get_itpr_estimate_for_team(project.id, team_member.team_id)
        
        # Apply team member allocation percentage
        member_allocation = team_member.allocation_percentage / 100.0
        estimate = estimate * member_allocation
        
        # If estimate is 0, check for core support hours
        if estimate == 0:
            estimate = self._get_core_support_hours(itpr_code)
        else:
            estimate = round(estimate, 0)
            if estimate == 0:
                estimate = 1
        
        # Distribute across weeks
        weekly_allocation = {}
        for week in weeks:
            weekly_allocation[week.isoformat()] = estimate
        
        return weekly_allocation
    
    def _get_itpr_estimate_for_team(self, project_id: int, team_id: int) -> float:
        """Get total hour estimate for ITPR and team"""
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return 0.0
        
        # Get all user stories for this project and team
        # Through: Project -> Epic -> Feature -> UserStory
        user_stories = self.db.query(UserStory).join(
            Feature
        ).join(
            Epic
        ).filter(
            and_(
                Epic.project_id == project_id,
                UserStory.team == team.name
            )
        ).all()
        
        total_sp = sum(us.plan_estimate for us in user_stories)
        total_hours = self.convert_story_points_to_hours(total_sp, team.name)
        
        # Calculate per week estimate
        weeks = self.rules["sprint_weeks"]["value"] * 5  # Assuming 5 sprints per PI
        per_week = self.calculate_hours_per_week(total_hours, team.name, weeks)
        
        return per_week
    
    def _get_core_support_hours(self, itpr_code: str) -> float:
        """Get core support hours for ITPR (from ITPR Owner sheet reference)"""
        # This would be configurable in the rules or a separate table
        # For now, return default
        return self.rules.get("default_core_support_hours", {"value": 5.0})["value"]
    
    def detect_project_overruns(self, project_id: int, sprint_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect project overruns (actual > planned)
        One of the key insights requested
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {}
        
        # Get planned hours (from allocations)
        planned_query = self.db.query(func.sum(TeamAllocation.allocated_hours)).filter(
            TeamAllocation.project_id == project_id
        )
        
        if sprint_name:
            sprint = self.db.query(Sprint).filter(Sprint.name == sprint_name).first()
            if sprint:
                planned_query = planned_query.filter(
                    and_(
                        TeamAllocation.week_start_date >= sprint.start_date,
                        TeamAllocation.week_start_date <= sprint.end_date
                    )
                )
        
        planned_hours = planned_query.scalar() or 0.0
        
        # Get actual hours (from time entries)
        actual_query = self.db.query(func.sum(TimeEntry.actual_hours)).filter(
            TimeEntry.project_id == project_id
        )
        
        if sprint_name:
            sprint = self.db.query(Sprint).filter(Sprint.name == sprint_name).first()
            if sprint:
                actual_query = actual_query.filter(
                    and_(
                        TimeEntry.week_start_date >= sprint.start_date,
                        TimeEntry.week_start_date <= sprint.end_date
                    )
                )
        
        actual_hours = actual_query.scalar() or 0.0
        
        overrun_hours = actual_hours - planned_hours
        overrun_percentage = (overrun_hours / planned_hours * 100) if planned_hours > 0 else 0
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "itpr_code": project.itpr_code,
            "planned_hours": planned_hours,
            "actual_hours": actual_hours,
            "overrun_hours": overrun_hours,
            "overrun_percentage": overrun_percentage,
            "is_overrun": overrun_hours > 0,
            "sprint": sprint_name
        }
    
    def detect_under_utilization(self, team_id: int, week_start: date) -> Dict[str, Any]:
        """
        Detect team under-utilization
        One of the key insights requested
        """
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return {}
        
        # Get team members
        members = self.db.query(TeamMember).filter(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.is_active == True
            )
        ).all()
        
        if not members:
            return {}
        
        # Calculate available hours
        hours_per_day = self.rules["hours_per_day"]["value"]
        working_days = self.rules["working_days_per_week"]["value"]
        available_hours_per_member = hours_per_day * working_days
        
        total_available_hours = 0
        for member in members:
            member_available = available_hours_per_member * (member.allocation_percentage / 100.0)
            total_available_hours += member_available
        
        # Get allocated hours for this week
        allocated_hours = self.db.query(func.sum(TeamAllocation.allocated_hours)).filter(
            and_(
                TeamAllocation.team_id == team_id,
                TeamAllocation.week_start_date == week_start
            )
        ).scalar() or 0.0
        
        utilization_percentage = (allocated_hours / total_available_hours * 100) if total_available_hours > 0 else 0
        under_utilized = utilization_percentage < 70  # Threshold for under-utilization
        
        return {
            "team_id": team_id,
            "team_name": team.name,
            "week_start": week_start.isoformat(),
            "available_hours": total_available_hours,
            "allocated_hours": allocated_hours,
            "utilization_percentage": utilization_percentage,
            "is_under_utilized": under_utilized,
            "team_members_count": len(members)
        }
    
    def forecast_project_completion(self, project_id: int) -> Dict[str, Any]:
        """
        Forecast project completion based on velocity
        One of the key insights requested
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return {}
        
        # Get all user stories for this project
        user_stories = self.db.query(UserStory).join(
            Feature
        ).join(
            Epic
        ).filter(
            Epic.project_id == project_id
        ).all()
        
        # Calculate remaining story points
        remaining_sp = sum(
            us.plan_estimate for us in user_stories 
            if us.state not in ["Completed", "Accepted"]
        )
        
        # Calculate velocity (completed SP in last 3 sprints)
        completed_sp_by_sprint = {}
        for us in user_stories:
            if us.state in ["Completed", "Accepted"] and us.iteration:
                if us.iteration not in completed_sp_by_sprint:
                    completed_sp_by_sprint[us.iteration] = 0
                completed_sp_by_sprint[us.iteration] += us.plan_estimate
        
        # Get last 3 sprints velocity
        recent_sprints = sorted(completed_sp_by_sprint.items(), key=lambda x: x[0], reverse=True)[:3]
        avg_velocity = sum(sp for _, sp in recent_sprints) / len(recent_sprints) if recent_sprints else 0
        
        # Estimate remaining sprints
        remaining_sprints = (remaining_sp / avg_velocity) if avg_velocity > 0 else float('inf')
        
        # Calculate estimated completion date
        current_sprint = self.db.query(Sprint).filter(Sprint.is_active == True).first()
        estimated_completion_date = None
        
        if current_sprint and remaining_sprints != float('inf'):
            days_per_sprint = (current_sprint.end_date - current_sprint.start_date).days
            estimated_completion_date = current_sprint.end_date + timedelta(days=int(remaining_sprints * days_per_sprint))
        
        # Determine confidence level and risks
        confidence_level = "High" if len(recent_sprints) >= 3 else "Medium" if len(recent_sprints) >= 2 else "Low"
        risks = []
        
        if remaining_sprints > 5:
            risks.append("High number of remaining sprints")
        if avg_velocity < 20:
            risks.append("Low team velocity")
        if project.end_date and estimated_completion_date and estimated_completion_date > project.end_date:
            risks.append("Estimated completion beyond project end date")
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "itpr_code": project.itpr_code,
            "remaining_story_points": remaining_sp,
            "average_velocity": avg_velocity,
            "estimated_remaining_sprints": remaining_sprints,
            "estimated_completion_date": estimated_completion_date.isoformat() if estimated_completion_date else None,
            "confidence_level": confidence_level,
            "risks": risks
        }
