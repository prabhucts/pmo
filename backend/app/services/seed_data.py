"""
Data Seeding Service
Loads default sample data into the database on first run
"""
from sqlalchemy.orm import Session
from pathlib import Path
import logging
from app.services.data_processor import DataProcessor

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


def seed_database(db: Session) -> dict:
    """
    Seed the database with sample data if it's empty.
    Returns a dict with seeding results.
    """
    from app.db.models import Project
    
    # Check if database already has data
    project_count = db.query(Project).count()
    if project_count > 0:
        logger.info("Database already contains data. Skipping seed.")
        return {
            "seeded": False,
            "reason": "Database already contains data",
            "projects": project_count
        }
    
    logger.info("Starting database seeding with sample data...")
    
    try:
        processor = DataProcessor(db)
        results = {}
        
        # Load Epics first (features and stories depend on epics/projects)
        epics_file = TEMPLATES_DIR / "rally_epics.csv"
        if epics_file.exists():
            epic_result = processor.process_epics(str(epics_file))
            results["epics"] = epic_result
            logger.info("Seeded %s epics", epic_result.get("rows_processed", 0))
        
        # Load Features
        features_file = TEMPLATES_DIR / "rally_features.csv"
        if features_file.exists():
            feature_result = processor.process_features(str(features_file))
            results["features"] = feature_result
            logger.info("Seeded %s features", feature_result.get("rows_processed", 0))
        
        # Load User Stories
        stories_file = TEMPLATES_DIR / "rally_userstories.csv"
        if stories_file.exists():
            story_result = processor.process_user_stories(str(stories_file))
            results["user_stories"] = story_result
            logger.info("Seeded %s user stories", story_result.get("rows_processed", 0))
        
        # Load Clarity Timesheet
        timesheet_file = TEMPLATES_DIR / "clarity_timesheet.csv"
        if timesheet_file.exists():
            timesheet_result = processor.process_clarity_timesheet(str(timesheet_file))
            results["timesheet"] = timesheet_result
            logger.info("Seeded %s timesheet entries", timesheet_result.get("rows_processed", 0))
        
        logger.info("Database seeding completed successfully")
        return {"seeded": True, "results": results}
        
    except Exception as e:
        logger.error("Error seeding database: %s", str(e))
        return {"seeded": False, "error": str(e)}


def check_and_seed_on_startup(db: Session) -> None:
    """Check if database needs seeding and seed it. Called during application startup."""
    try:
        result = seed_database(db)
        if result.get("seeded"):
            logger.info("Database seeded with sample data")
        else:
            logger.info("Seeding skipped: %s", result.get("reason", result.get("error", "Unknown")))
    except Exception as e:
        logger.error("Error during startup seeding: %s", str(e))
