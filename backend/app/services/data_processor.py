"""
Data processor for importing Rally and Clarity data
"""
import pandas as pd
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.db.models import (
    Project, Epic, Feature, UserStory, Defect,
    Team, TeamMember, TeamAllocation, Sprint
)

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and import data from CSV/Excel files"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def process_user_stories(self, file_path: str) -> Dict[str, Any]:
        """
        Process user stories from Rally export
        Expected columns: Formatted ID, Name, Owner, Parent, Portfolio Item, Feature, 
                         Project, Release, Iteration, Plan Estimate
        """
        try:
            df = pd.read_csv(file_path)
            
            # Validate required columns
            required_cols = ["Formatted ID", "Name", "Project", "Plan Estimate"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return {
                    "success": False,
                    "error": f"Missing columns: {', '.join(missing_cols)}"
                }
            
            rows_processed = 0
            rows_skipped = 0
            
            for _, row in df.iterrows():
                try:
                    # Get or create feature if exists
                    feature_id = None
                    if pd.notna(row.get("Feature")):
                        feature_formatted_id = self._extract_formatted_id(str(row["Feature"]))
                        feature = self.db.query(Feature).filter(
                            Feature.formatted_id == feature_formatted_id
                        ).first()
                        if feature:
                            feature_id = feature.id
                    
                    # Check if user story already exists
                    existing = self.db.query(UserStory).filter(
                        UserStory.formatted_id == row["Formatted ID"]
                    ).first()
                    
                    if existing:
                        # Update existing
                        existing.name = row["Name"]
                        existing.owner = row.get("Owner")
                        existing.team = row.get("Project")
                        existing.release = row.get("Release")
                        existing.iteration = row.get("Iteration")
                        existing.plan_estimate = float(row["Plan Estimate"]) if pd.notna(row["Plan Estimate"]) else 0.0
                        existing.feature_id = feature_id
                    else:
                        # Create new
                        user_story = UserStory(
                            formatted_id=row["Formatted ID"],
                            name=row["Name"],
                            owner=row.get("Owner"),
                            team=row.get("Project"),
                            release=row.get("Release"),
                            iteration=row.get("Iteration"),
                            plan_estimate=float(row["Plan Estimate"]) if pd.notna(row["Plan Estimate"]) else 0.0,
                            feature_id=feature_id
                        )
                        self.db.add(user_story)
                    
                    rows_processed += 1
                except Exception as e:
                    logger.error(f"Error processing row: {e}")
                    rows_skipped += 1
                    continue
            
            self.db.commit()
            
            return {
                "success": True,
                "rows_processed": rows_processed,
                "rows_skipped": rows_skipped,
                "file_type": "user_stories"
            }
        
        except Exception as e:
            logger.error(f"Error processing user stories: {e}")
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_features(self, file_path: str) -> Dict[str, Any]:
        """
        Process features from Rally export
        Expected columns: Formatted ID, Name, Owner, Parent, Project, Release
        """
        try:
            df = pd.read_csv(file_path)
            
            required_cols = ["Formatted ID", "Name"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return {
                    "success": False,
                    "error": f"Missing columns: {', '.join(missing_cols)}"
                }
            
            rows_processed = 0
            rows_skipped = 0
            
            for _, row in df.iterrows():
                try:
                    # Get or create epic if exists
                    epic_id = None
                    if pd.notna(row.get("Parent")):
                        epic_formatted_id = self._extract_formatted_id(str(row["Parent"]))
                        epic = self.db.query(Epic).filter(
                            Epic.formatted_id == epic_formatted_id
                        ).first()
                        if epic:
                            epic_id = epic.id
                    
                    # Check if feature already exists
                    existing = self.db.query(Feature).filter(
                        Feature.formatted_id == row["Formatted ID"]
                    ).first()
                    
                    if existing:
                        existing.name = row["Name"]
                        existing.owner = row.get("Owner")
                        existing.release = row.get("Release")
                        existing.epic_id = epic_id
                    else:
                        feature = Feature(
                            formatted_id=row["Formatted ID"],
                            name=row["Name"],
                            owner=row.get("Owner"),
                            release=row.get("Release"),
                            epic_id=epic_id
                        )
                        self.db.add(feature)
                    
                    rows_processed += 1
                except Exception as e:
                    logger.error(f"Error processing row: {e}")
                    rows_skipped += 1
                    continue
            
            self.db.commit()
            
            return {
                "success": True,
                "rows_processed": rows_processed,
                "rows_skipped": rows_skipped,
                "file_type": "features"
            }
        
        except Exception as e:
            logger.error(f"Error processing features: {e}")
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_epics(self, file_path: str) -> Dict[str, Any]:
        """
        Process epics from Rally export
        Expected columns: Formatted ID, Name, State, Project, Owner, Parent
        """
        try:
            df = pd.read_csv(file_path)
            
            required_cols = ["Formatted ID", "Name"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return {
                    "success": False,
                    "error": f"Missing columns: {', '.join(missing_cols)}"
                }
            
            rows_processed = 0
            rows_skipped = 0
            
            for _, row in df.iterrows():
                try:
                    # Get or create project from Parent field (ITPR)
                    project_id = None
                    if pd.notna(row.get("Parent")):
                        itpr_code = self._extract_itpr_code(str(row["Parent"]))
                        if itpr_code:
                            project = self.db.query(Project).filter(
                                Project.itpr_code == itpr_code
                            ).first()
                            
                            if not project:
                                # Create project
                                project = Project(
                                    itpr_code=itpr_code,
                                    name=str(row["Parent"]),
                                    theme=self._extract_theme(str(row["Parent"]))
                                )
                                self.db.add(project)
                                self.db.flush()
                            
                            project_id = project.id
                    
                    # Check if epic already exists
                    existing = self.db.query(Epic).filter(
                        Epic.formatted_id == row["Formatted ID"]
                    ).first()
                    
                    if existing:
                        existing.name = row["Name"]
                        existing.state = row.get("State")
                        existing.owner = row.get("Owner")
                        existing.project_id = project_id
                    else:
                        epic = Epic(
                            formatted_id=row["Formatted ID"],
                            name=row["Name"],
                            state=row.get("State"),
                            owner=row.get("Owner"),
                            project_id=project_id
                        )
                        self.db.add(epic)
                    
                    rows_processed += 1
                except Exception as e:
                    logger.error(f"Error processing row: {e}")
                    rows_skipped += 1
                    continue
            
            self.db.commit()
            
            return {
                "success": True,
                "rows_processed": rows_processed,
                "rows_skipped": rows_skipped,
                "file_type": "epics"
            }
        
        except Exception as e:
            logger.error(f"Error processing epics: {e}")
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_clarity_timesheet(self, file_path: str) -> Dict[str, Any]:
        """
        Process Clarity timesheet data
        Expected columns: Team, Initiative, Resource Name, Network ID, Location, 
                         and weekly columns with dates
        """
        try:
            df = pd.read_csv(file_path)
            
            # Validate required columns
            required_cols = ["Team", "Resource Name (in Clarity)"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return {
                    "success": False,
                    "error": f"Missing columns: {', '.join(missing_cols)}"
                }
            
            rows_processed = 0
            rows_skipped = 0
            
            # Get date columns (columns that can be parsed as dates)
            date_columns = []
            for col in df.columns:
                try:
                    pd.to_datetime(col)
                    date_columns.append(col)
                except:
                    pass
            
            for _, row in df.iterrows():
                try:
                    # Get or create team
                    team_name = row["Team"]
                    team = self.db.query(Team).filter(Team.name == team_name).first()
                    if not team:
                        team = Team(name=team_name)
                        self.db.add(team)
                        self.db.flush()
                    
                    # Get or create team member
                    member_name = row["Resource Name (in Clarity)"]
                    member_email = row.get("Network ID or email Location", f"{member_name.replace(' ', '_').lower()}@company.com")
                    
                    member = self.db.query(TeamMember).filter(
                        TeamMember.email == member_email
                    ).first()
                    
                    if not member:
                        member = TeamMember(
                            name=member_name,
                            email=member_email,
                            network_id=row.get("Network ID or email Location"),
                            location=row.get("Location"),
                            team_id=team.id
                        )
                        self.db.add(member)
                        self.db.flush()
                    
                    # Get or create project
                    if pd.notna(row.get("Initiative (Use Dropdown of Current ITPRs)")):
                        itpr_code = self._extract_itpr_code(str(row["Initiative (Use Dropdown of Current ITPRs)"]))
                        if itpr_code:
                            project = self.db.query(Project).filter(
                                Project.itpr_code == itpr_code
                            ).first()
                            
                            if not project:
                                project = Project(
                                    itpr_code=itpr_code,
                                    name=str(row["Initiative (Use Dropdown of Current ITPRs)"])
                                )
                                self.db.add(project)
                                self.db.flush()
                            
                            # Process weekly allocations
                            for date_col in date_columns:
                                if pd.notna(row[date_col]):
                                    week_start = pd.to_datetime(date_col).date()
                                    hours = float(row[date_col])
                                    
                                    # Check if allocation exists
                                    existing = self.db.query(TeamAllocation).filter(
                                        and_(
                                            TeamAllocation.team_member_id == member.id,
                                            TeamAllocation.project_id == project.id,
                                            TeamAllocation.week_start_date == week_start
                                        )
                                    ).first()
                                    
                                    if existing:
                                        existing.allocated_hours = hours
                                    else:
                                        allocation = TeamAllocation(
                                            team_id=team.id,
                                            project_id=project.id,
                                            team_member_id=member.id,
                                            week_start_date=week_start,
                                            allocated_hours=hours
                                        )
                                        self.db.add(allocation)
                    
                    rows_processed += 1
                except Exception as e:
                    logger.error(f"Error processing row: {e}")
                    rows_skipped += 1
                    continue
            
            self.db.commit()
            
            return {
                "success": True,
                "rows_processed": rows_processed,
                "rows_skipped": rows_skipped,
                "file_type": "clarity_timesheet"
            }
        
        except Exception as e:
            logger.error(f"Error processing clarity timesheet: {e}")
            self.db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_formatted_id(self, text: str) -> str:
        """Extract formatted ID from text (e.g., 'Feature F214458: ...' -> 'F214458')"""
        import re
        match = re.search(r'([FE]\d+)', text)
        return match.group(1) if match else text
    
    def _extract_itpr_code(self, text: str) -> str:
        """Extract ITPR code from text (e.g., 'ITPR082135 - ...' -> 'ITPR082135')"""
        import re
        match = re.search(r'(ITPR\d+)', text)
        return match.group(1) if match else ""
    
    def _extract_theme(self, text: str) -> str:
        """Extract theme from text (e.g., 'Theme T4426: ...' -> 'T4426')"""
        import re
        match = re.search(r'Theme (T\d+)', text)
        return match.group(1) if match else ""
