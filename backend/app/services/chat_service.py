"""
AI Chat Service using OpenAI
"""
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, date
import logging

from openai import OpenAI

from app.core.config import settings
from app.db.models import ChatHistory, Project, Team, UserStory, Sprint, Insight
from app.services.business_rules import BusinessRulesEngine

logger = logging.getLogger(__name__)


class ChatService:
    """AI-powered chat service for PMO insights"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rules_engine = BusinessRulesEngine(db)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        
        # Intent classification system prompt
        self.intent_system_prompt = """You are an AI assistant for a PMO operations system. 
Classify the user's intent into one of these categories:
- project_overrun: Questions about project overruns or budget issues
- under_utilization: Questions about team under-utilization or capacity
- team_hours: Questions about team hour entry or tracking
- forecast: Questions about project forecasting or completion dates
- sprint_status: Questions about sprint status or progress
- project_info: General project information queries
- team_info: General team information queries
- data_query: Specific data queries
- general: General questions or help

Respond with ONLY the intent category and any extracted parameters in JSON format.
Example: {"intent": "project_overrun", "parameters": {"project": "ITPR082135", "sprint": "2026.S1"}}"""
    
    def process_message(self, message: str, session_id: str) -> Dict[str, Any]:
        """Process incoming chat message"""
        try:
            # Classify intent
            intent_data = self._classify_intent(message)
            intent = intent_data.get("intent", "general")
            parameters = intent_data.get("parameters", {})
            
            # Route to appropriate handler
            if intent == "project_overrun":
                response = self._handle_project_overrun(parameters)
            elif intent == "under_utilization":
                response = self._handle_under_utilization(parameters)
            elif intent == "team_hours":
                response = self._handle_team_hours(parameters)
            elif intent == "forecast":
                response = self._handle_forecast(parameters)
            elif intent == "sprint_status":
                response = self._handle_sprint_status(parameters)
            elif intent == "project_info":
                response = self._handle_project_info(parameters)
            elif intent == "team_info":
                response = self._handle_team_info(parameters)
            else:
                response = self._handle_general(message, session_id)
            
            # Save to history
            self._save_chat_history(session_id, message, response["text"], intent, response.get("data"))
            
            return {
                "response": response["text"],
                "intent": intent,
                "data": response.get("data"),
                "session_id": session_id
            }
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "intent": "error",
                "data": {"error": str(e)},
                "session_id": session_id
            }
    
    def _classify_intent(self, message: str) -> Dict[str, Any]:
        """Classify user intent"""
        if not self.client:
            # Fallback to keyword-based classification
            return self._keyword_based_intent(message)
        
        try:
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.intent_system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.3,
                max_tokens=200
            )
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return self._keyword_based_intent(message)
    
    def _keyword_based_intent(self, message: str) -> Dict[str, Any]:
        """Fallback keyword-based intent classification"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["overrun", "over budget", "exceeded"]):
            return {"intent": "project_overrun", "parameters": {}}
        elif any(word in message_lower for word in ["under-util", "underutil", "capacity", "idle"]):
            return {"intent": "under_utilization", "parameters": {}}
        elif any(word in message_lower for word in ["hours", "timesheet", "time entry", "logging"]):
            return {"intent": "team_hours", "parameters": {}}
        elif any(word in message_lower for word in ["forecast", "completion", "when will", "estimate"]):
            return {"intent": "forecast", "parameters": {}}
        elif any(word in message_lower for word in ["sprint", "iteration"]):
            return {"intent": "sprint_status", "parameters": {}}
        elif any(word in message_lower for word in ["project", "itpr"]):
            return {"intent": "project_info", "parameters": {}}
        elif any(word in message_lower for word in ["team", "member"]):
            return {"intent": "team_info", "parameters": {}}
        else:
            return {"intent": "general", "parameters": {}}
    
    def _handle_project_overrun(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project overrun queries"""
        project_code = parameters.get("project")
        sprint_name = parameters.get("sprint")
        
        if project_code:
            # Specific project
            project = self.db.query(Project).filter(
                Project.itpr_code == project_code
            ).first()
            
            if not project:
                return {
                    "text": f"I couldn't find project {project_code}. Please check the ITPR code.",
                    "data": {}
                }
            
            overrun_data = self.rules_engine.detect_project_overruns(project.id, sprint_name)
            
            if overrun_data["is_overrun"]:
                text = f"**Project Overrun Detected**\n\n"
                text += f"Project: {overrun_data['project_name']} ({overrun_data['itpr_code']})\n"
                text += f"Planned Hours: {overrun_data['planned_hours']:.1f}\n"
                text += f"Actual Hours: {overrun_data['actual_hours']:.1f}\n"
                text += f"Overrun: {overrun_data['overrun_hours']:.1f} hours ({overrun_data['overrun_percentage']:.1f}%)\n"
                
                if sprint_name:
                    text += f"Sprint: {sprint_name}\n"
            else:
                text = f"Project {overrun_data['project_name']} is within planned hours. "
                text += f"Planned: {overrun_data['planned_hours']:.1f}, Actual: {overrun_data['actual_hours']:.1f}"
            
            return {"text": text, "data": overrun_data}
        else:
            # All projects with overruns
            projects = self.db.query(Project).filter(Project.status == "Active").all()
            overruns = []
            
            for project in projects:
                overrun_data = self.rules_engine.detect_project_overruns(project.id, sprint_name)
                if overrun_data["is_overrun"]:
                    overruns.append(overrun_data)
            
            if overruns:
                text = f"**Found {len(overruns)} projects with overruns:**\n\n"
                for overrun in overruns[:5]:  # Show top 5
                    text += f"- {overrun['project_name']} ({overrun['itpr_code']}): "
                    text += f"+{overrun['overrun_hours']:.1f} hours ({overrun['overrun_percentage']:.1f}%)\n"
                
                if len(overruns) > 5:
                    text += f"\n...and {len(overruns) - 5} more"
            else:
                text = "Great news! No projects are currently showing overruns."
            
            return {"text": text, "data": {"overruns": overruns}}
    
    def _handle_under_utilization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle team under-utilization queries"""
        teams = self.db.query(Team).all()
        current_week = date.today()
        
        under_utilized = []
        
        for team in teams:
            util_data = self.rules_engine.detect_under_utilization(team.id, current_week)
            if util_data.get("is_under_utilized"):
                under_utilized.append(util_data)
        
        if under_utilized:
            text = f"**Under-Utilized Teams (< 70% capacity):**\n\n"
            for util in under_utilized:
                text += f"- {util['team_name']}: {util['utilization_percentage']:.1f}% "
                text += f"({util['allocated_hours']:.1f}/{util['available_hours']:.1f} hours)\n"
        else:
            text = "All teams are well-utilized (>= 70% capacity)."
        
        return {"text": text, "data": {"under_utilized": under_utilized}}
    
    def _handle_team_hours(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle team hour tracking queries"""
        from app.db.models import TeamMember, TimeEntry
        
        current_week = date.today()
        
        # Get all active team members
        members = self.db.query(TeamMember).filter(TeamMember.is_active == True).all()
        
        # Check who has entered hours this week
        members_with_hours = []
        members_without_hours = []
        
        for member in members:
            has_hours = self.db.query(TimeEntry).filter(
                and_(
                    TimeEntry.team_member_id == member.id,
                    TimeEntry.week_start_date == current_week
                )
            ).first() is not None
            
            if has_hours:
                members_with_hours.append(member.name)
            else:
                members_without_hours.append(member.name)
        
        text = f"**Hour Entry Status (Week of {current_week}):**\n\n"
        text += f"✅ Entered: {len(members_with_hours)} team members\n"
        text += f"❌ Not Entered: {len(members_without_hours)} team members\n\n"
        
        if members_without_hours and len(members_without_hours) <= 10:
            text += "**Members who haven't entered hours:**\n"
            for name in members_without_hours[:10]:
                text += f"- {name}\n"
        
        return {
            "text": text,
            "data": {
                "with_hours": members_with_hours,
                "without_hours": members_without_hours
            }
        }
    
    def _handle_forecast(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project forecast queries"""
        project_code = parameters.get("project")
        
        if project_code:
            project = self.db.query(Project).filter(
                Project.itpr_code == project_code
            ).first()
            
            if not project:
                return {
                    "text": f"I couldn't find project {project_code}.",
                    "data": {}
                }
            
            forecast = self.rules_engine.forecast_project_completion(project.id)
            
            text = f"**Forecast for {forecast['project_name']} ({forecast['itpr_code']}):**\n\n"
            text += f"Remaining Story Points: {forecast['remaining_story_points']:.1f}\n"
            text += f"Average Velocity: {forecast['average_velocity']:.1f} SP/sprint\n"
            text += f"Estimated Sprints Remaining: {forecast['estimated_remaining_sprints']:.1f}\n"
            
            if forecast['estimated_completion_date']:
                text += f"Estimated Completion: {forecast['estimated_completion_date']}\n"
            
            text += f"Confidence Level: {forecast['confidence_level']}\n"
            
            if forecast['risks']:
                text += f"\n**Risks:**\n"
                for risk in forecast['risks']:
                    text += f"- {risk}\n"
            
            return {"text": text, "data": forecast}
        else:
            return {
                "text": "Please specify a project ITPR code for forecasting.",
                "data": {}
            }
    
    def _handle_sprint_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sprint status queries"""
        sprint_name = parameters.get("sprint")
        
        if sprint_name:
            sprint = self.db.query(Sprint).filter(Sprint.name == sprint_name).first()
        else:
            sprint = self.db.query(Sprint).filter(Sprint.is_active == True).first()
        
        if not sprint:
            return {"text": "No active sprint found.", "data": {}}
        
        # Get user stories for this sprint
        user_stories = self.db.query(UserStory).filter(
            UserStory.iteration == sprint.name
        ).all()
        
        total_sp = sum(us.plan_estimate for us in user_stories)
        completed_sp = sum(
            us.plan_estimate for us in user_stories 
            if us.state in ["Completed", "Accepted"]
        )
        
        text = f"**Sprint Status: {sprint.name}**\n\n"
        text += f"Period: {sprint.start_date} to {sprint.end_date}\n"
        text += f"Total Story Points: {total_sp:.1f}\n"
        text += f"Completed: {completed_sp:.1f} ({(completed_sp/total_sp*100):.1f}%)\n"
        text += f"Remaining: {total_sp - completed_sp:.1f}\n"
        text += f"User Stories: {len(user_stories)}\n"
        
        return {
            "text": text,
            "data": {
                "sprint": sprint.name,
                "total_sp": total_sp,
                "completed_sp": completed_sp,
                "remaining_sp": total_sp - completed_sp
            }
        }
    
    def _handle_project_info(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project information queries"""
        projects = self.db.query(Project).filter(Project.status == "Active").limit(10).all()
        
        text = f"**Active Projects ({len(projects)}):**\n\n"
        for project in projects:
            text += f"- {project.name} ({project.itpr_code})\n"
            if project.owner:
                text += f"  Owner: {project.owner}\n"
        
        return {"text": text, "data": {}}
    
    def _handle_team_info(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle team information queries"""
        teams = self.db.query(Team).all()
        
        text = f"**Teams ({len(teams)}):**\n\n"
        for team in teams:
            member_count = self.db.query(TeamMember).filter(
                and_(
                    TeamMember.team_id == team.id,
                    TeamMember.is_active == True
                )
            ).count()
            text += f"- {team.name}: {member_count} members\n"
        
        return {"text": text, "data": {}}
    
    def _handle_general(self, message: str, session_id: str) -> Dict[str, Any]:
        """Handle general queries with OpenAI"""
        if not self.client:
            return {
                "text": "I can help you with:\n"
                        "- Project overruns\n"
                        "- Team under-utilization\n"
                        "- Hour entry tracking\n"
                        "- Project forecasting\n"
                        "- Sprint status\n\n"
                        "What would you like to know?",
                "data": {}
            }
        
        try:
            # Use OpenAI for general conversation
            system_prompt = """You are an AI assistant for a PMO operations system. 
You help project managers understand their data and make informed decisions.
Be helpful, concise, and professional."""
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return {"text": response.choices[0].message.content, "data": {}}
        except Exception as e:
            logger.error(f"Error in general handler: {e}")
            return {
                "text": "I'm here to help with PMO insights. What would you like to know?",
                "data": {}
            }
    
    def _save_chat_history(
        self, 
        session_id: str, 
        user_message: str, 
        bot_response: str,
        intent: str,
        context: Optional[Dict] = None
    ):
        """Save chat history to database"""
        try:
            history = ChatHistory(
                session_id=session_id,
                user_message=user_message,
                bot_response=bot_response,
                intent=intent,
                context=context or {}
            )
            self.db.add(history)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
            self.db.rollback()
