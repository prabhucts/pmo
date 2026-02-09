# Sample Data Files

This directory contains comprehensive sample CSV files for testing the PMO Operations Solution.

## Files Included

### 1. rally_epics.csv
Contains Epic-level data with proper ITPR/Theme mappings.

**Columns:**
- Formatted ID (e.g., E26575)
- Name
- State (Implementing, Planning, etc.)
- Percent Done By Story Plan Estimate
- Percent Done By Story Count
- Project
- Owner
- Preliminary Estimate (S, M, L, XL)
- Tags
- Parent (Theme T####: ITPR###### - Description)

**Records:** 13 Epics mapped to 8 different ITPRs

### 2. rally_features.csv
Contains Feature-level data linking to Epics.

**Columns:**
- Formatted ID (e.g., F214458)
- Name
- Owner
- Parent (Epic reference)
- Project
- Release
- State

**Records:** 28 Features distributed across the Epics

### 3. rally_userstories.csv
Contains User Story-level data with estimates.

**Columns:**
- Formatted ID (e.g., US2168698)
- Name
- Owner
- Parent
- Portfolio Item
- Feature (reference to Feature)
- Project (Team name: Audi, Chrysler, Jaguars, Mercedes, Rivian, Rolls Royce)
- Release (2026.Jan, 2026.Feb, 2025.PI4)
- Iteration (Sprint: 2026.S1, 2026.S2)
- Plan Estimate (Story Points: 0-8)
- State (Defined, In-Progress, Completed, Accepted)

**Records:** 68 User Stories with various states and story point estimates

### 4. clarity_timesheet.csv
Contains team allocation data by week.

**Columns:**
- Team (Audi, Chrysler, Jaguars, Mercedes, Rivian, Rolls Royce)
- Initiative with THEME
- Initiative (Use Dropdown of Current ITPRs)
- PMO Owner
- Missing from Clarity assignment
- Resource Name (in Clarity)
- Network ID or email Location
- Location (Onsite/Offshore)
- Weekly date columns (12/30/2025 through 2/24/2026)

**Records:** 55+ team member allocations across 6 teams and multiple projects

## Data Relationships

### Hierarchy
```
ITPR (Project)
  └─ Epic
      └─ Feature
          └─ User Story
```

### Teams and Projects
- **Audi**: 5 members (3 Offshore, 2 Onsite)
- **Chrysler**: 5 members (All Onsite)
- **Jaguars**: 3 members (2 Offshore, 1 Onsite)
- **Mercedes**: 2 members (1 Onsite, 1 Offshore)
- **Rivian**: 2 members (All Offshore)
- **Rolls Royce**: 2 members (All Offshore)

### Key ITPRs (Projects)
1. **ITPR082135** - AHM RTB - Data Platform & Config
2. **ITPR082125** - AHM RTB - MAH Member Experience Enhancements
3. **ITPR082127** - AHM RTB - TMV KTLO
4. **ITPR082148** - AHM L3 - MAH
5. **ITPR080952** - Metabolic Health Revamp Program
6. **ITPR076393** - PLSS AHM-Core Support
7. **ITPR078922** - PLSS RTB-2025 ODS ETL Migration to Cloud
8. **ITPR082124** - AHM RTB - LCC Enhancements

## Data Integrity

### Referential Integrity
✅ All User Stories reference valid Features
✅ All Features reference valid Epics
✅ All Epics reference valid ITPRs (Projects)
✅ All team allocations reference valid ITPRs

### Story Points Distribution
- **Total Story Points:** 280 SP across all user stories
- **Completed:** ~150 SP (54%)
- **In Progress:** ~80 SP (29%)
- **Defined:** ~50 SP (18%)

### Sprint Distribution
- **2026.S1:** ~170 SP (Sprint 1)
- **2026.S2:** ~110 SP (Sprint 2)

### Team Distribution
- **Chrysler:** ~90 SP
- **Audi:** ~75 SP
- **Mercedes:** ~40 SP
- **Jaguars:** ~35 SP
- **Rivian:** ~25 SP
- **Rolls Royce:** ~15 SP

## Usage

### Upload via Web UI
1. Start the application
2. Navigate to http://localhost:3000/upload
3. Upload files in this order:
   - rally_epics.csv (creates Projects)
   - rally_features.csv (creates Features)
   - rally_userstories.csv (creates User Stories)
   - clarity_timesheet.csv (creates Teams and Allocations)

### Upload via API
```bash
# Epics
curl -X POST http://localhost:8000/api/uploads/epics \
  -F "file=@data/rally_epics.csv"

# Features
curl -X POST http://localhost:8000/api/uploads/features \
  -F "file=@data/rally_features.csv"

# User Stories
curl -X POST http://localhost:8000/api/uploads/user-stories \
  -F "file=@data/rally_userstories.csv"

# Clarity Timesheet
curl -X POST http://localhost:8000/api/uploads/clarity-timesheet \
  -F "file=@data/clarity_timesheet.csv"
```

## Expected Results

After uploading all files, you should see:
- **8 Projects** (ITPRs)
- **13 Epics**
- **28 Features**
- **68 User Stories**
- **6 Teams**
- **19 Team Members**
- **280+ Total Story Points**
- **55+ Team Allocations**

## Business Rule Testing

This data is designed to test:

1. **Story Point Conversion**: 280 SP × 13 hours = 3,640 hours
2. **Team Allocation**: Multiple team members per project
3. **Sprint Planning**: Work distributed across 2 sprints
4. **Project Overruns**: Varied allocations to test detection
5. **Under-Utilization**: Some teams with lower allocations
6. **Forecasting**: Mix of completed and remaining work
7. **Defect Tracking**: L3 defects included
8. **Multi-team Projects**: Projects spanning multiple teams

## Sample Queries for AI Chat

Try these questions after uploading:

1. "Show me projects with the most story points"
2. "Which teams are working on ITPR082135?"
3. "What's the status of Sprint 2026.S1?"
4. "How many story points has Chrysler completed?"
5. "Forecast completion for ITPR082125"
6. "Which features are in progress?"
7. "Show team utilization for Audi"
8. "What are the top 5 user stories by story points?"

## Notes

- All dates use format MM/DD/YYYY or YYYY.MM
- Story points range from 0 to 8
- Hours per week reflect realistic team capacity
- Some user stories have 0 story points (definition or spike work)
- State values match Rally's standard workflow
