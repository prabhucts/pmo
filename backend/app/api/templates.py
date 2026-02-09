"""
Template Download API
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import os

router = APIRouter()

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"

AVAILABLE_TEMPLATES = {
    "rally_epics": "rally_epics.csv",
    "rally_features": "rally_features.csv",
    "rally_userstories": "rally_userstories.csv",
    "clarity_timesheet": "clarity_timesheet.csv"
}


@router.get("/list")
async def list_templates():
    """List all available template files"""
    templates = []
    for key, filename in AVAILABLE_TEMPLATES.items():
        filepath = TEMPLATES_DIR / filename
        if filepath.exists():
            templates.append({
                "id": key,
                "filename": filename,
                "size": os.path.getsize(filepath),
                "description": get_template_description(key)
            })
    return {"templates": templates}


@router.get("/download/{template_id}")
async def download_template(template_id: str):
    """Download a specific template file"""
    if template_id not in AVAILABLE_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    filename = AVAILABLE_TEMPLATES[template_id]
    filepath = TEMPLATES_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Template file not found")
    
    return FileResponse(
        path=filepath,
        media_type="text/csv",
        filename=filename,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


def get_template_description(template_id: str) -> str:
    """Get description for each template"""
    descriptions = {
        "rally_epics": "Rally Epics template with project mapping (ITPR)",
        "rally_features": "Rally Features template linked to Epics",
        "rally_userstories": "Rally User Stories with story points and sprint assignments",
        "clarity_timesheet": "Clarity timesheet data with team allocations by week"
    }
    return descriptions.get(template_id, "Template file")
