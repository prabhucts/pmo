# Business Rules Extracted from VBA Modules

This document describes the business rules and logic extracted from Module1.vba and Module2.vba.

## 1. Conversion Rules

### Story Point to Hours
- **Default**: 1 Story Point = 13 hours
- **Configurable**: Can be set per team in business rules
- **Source**: VBA line 469 - `Sp_Hours = VLookup(searchvalue, ws_ref, 6, 1)`
- **Application**: Used for all user story estimates and defect estimates

### Sprint Duration
- **Default**: 2 weeks = 10 working days
- **Source**: VBA Module2, line 40 - `sprintEndDate = DateAdd("d", 13, sprint_start)`
- **Working Days**: 5 days per week
- **Hours per Day**: 8 hours (configurable)

## 2. Team Allocation Rules

### Rally Allocation Percentage
- Each team member has an allocation percentage (e.g., 50%, 75%, 100%)
- Team rally allocation = Average of all team member allocations
- **Source**: VBA lines 374-377
  ```vb
  rally_all = SumIfs10(ws_Teams, lastRow_ws_Teams, 8, criteria1, 1)
  rally_all = rally_all / 100
  ws_ref.Cells(resultfRow, 5).value = rally_all
  ```

### Team Member Distribution
- Hours calculated per team = Total hours / Team size / Rally allocation
- **Source**: VBA lines 729-732
  ```vb
  If teamcount > 0 Then
      CalculateHours = sumResult / weeks / teamcount
  Else
      CalculateHours = 0
  End If
  ```

## 3. Defect Handling

### Defect Estimation
Defects are linked to features or user stories:
1. Check if defect has a direct feature link (Portfolio Item field)
2. If not, extract user story from Requirement field and link to feature
3. Add defect estimate to feature total

**Source**: VBA lines 739-805 (defectestimate function)

### L3 Defects
- Special handling for L3 defects
- No feature or user story link
- Tracked separately under "L3 defect" ITPR
- **Source**: VBA lines 498-550

## 4. Clarity Allocation Calculation

### Per-Week Allocation
For each team member and ITPR:
1. Calculate total hours from story points
2. Apply team rally allocation percentage
3. Apply individual member allocation percentage
4. Distribute across weeks in the PI/Sprint

**Source**: VBA lines 564-611 (ClaritySheet function)

### Core Support Hours
If calculated estimate is 0:
- Use default core support hours from ITPR Owner reference
- Typically 5 hours per week
- **Source**: VBA lines 592-602

### Minimum Allocation
- If calculated estimate rounds to 0, set to 1 hour
- **Source**: VBA lines 597-600

## 5. Summary Calculations

### Feature-Level Summary
For each Feature and Team:
1. Sum all user story estimates
2. Add related defect estimates
3. Convert story points to hours
4. Calculate per-week hours based on PI duration

**Source**: VBA lines 458-492

### ITPR-Level Summary
- Aggregate all features under each Epic
- Aggregate all Epics under each ITPR
- Track by team

## 6. Validation Rules

### Data Mapping
1. **User Story → Feature**: Via "Feature" column
2. **Feature → Epic**: Via "Parent" column (extract F##### from text)
3. **Epic → ITPR**: Via "Parent" column (extract ITPR###### from text)

### Reference Data
- Sprint calendar with start/end dates
- Team member roster with roles and allocations
- ITPR owner mapping

## 7. Insights Rules

### Project Overruns
**Trigger**: Actual hours > Planned hours

**Calculation**:
```
Planned Hours = SUM(Clarity Allocations for project)
Actual Hours = SUM(Time Entries for project)
Overrun = Actual - Planned
Overrun % = (Overrun / Planned) * 100
```

**Severity**:
- Warning: Overrun < 20%
- Critical: Overrun >= 20%

### Under-Utilization
**Trigger**: Team utilization < 70%

**Calculation**:
```
Available Hours = Team Members * Hours/Day * Days/Week * Allocation%
Allocated Hours = SUM(Clarity Allocations for team)
Utilization % = (Allocated / Available) * 100
```

### Project Ended but Allocation Exists
**Trigger**: Project status = "Completed" but Clarity allocations exist

**Check**:
- Compare project end date with current date
- Check for allocations after end date

### Team Hour Entry Tracking
**Trigger**: Team member has no time entries for current week

**Check**:
- For each active team member
- Check if time entries exist for week_start_date = current week

## 8. Forecasting Rules

### Velocity Calculation
Average story points completed in last 3 sprints:
```
Velocity = (Sprint1_Completed + Sprint2_Completed + Sprint3_Completed) / 3
```

### Remaining Work
```
Remaining SP = SUM(User Stories where State NOT IN ['Completed', 'Accepted'])
```

### Estimated Completion
```
Remaining Sprints = Remaining SP / Velocity
Estimated Date = Current Sprint End + (Remaining Sprints * Sprint Duration)
```

### Confidence Level
- High: 3 or more historical sprints
- Medium: 2 historical sprints
- Low: 1 or fewer historical sprints

### Risk Factors
- High remaining sprints (> 5)
- Low velocity (< 20 SP/sprint)
- Estimated completion beyond project end date

## 9. Data Processing Rules

### Import Priority
1. Epics (creates Projects/ITPRs)
2. Features (links to Epics)
3. User Stories (links to Features)
4. Defects (links to Features or User Stories)
5. Clarity Timesheet (creates Teams, Members, Allocations)

### Data Validation
- Required fields must not be empty
- Story points must be numeric
- Dates must be valid format
- ITPR codes must match pattern: ITPR######

### Error Handling
- Skip rows with missing required data
- Log errors for review
- Continue processing remaining rows
- Report summary of processed/skipped rows

## 10. Sprint Planning Rules

### Sprint Creation
From Module2.vba:
- Sprint start date from reference
- Sprint end date = start + 13 days
- Week start = Monday of sprint week
- Sprint name format: "YYYY.S#" (e.g., "2026.S1")

### Week Mapping
Each sprint spans 2 weeks:
- Week 1: Days 1-7
- Week 2: Days 8-14 (partial)

## Configurable Parameters

All these rules can be configured via the Business Rules UI:

| Parameter | Default | Description |
|-----------|---------|-------------|
| story_point_hours | 13 | Hours per story point |
| sprint_weeks | 2 | Weeks per sprint |
| working_days_per_week | 5 | Working days |
| hours_per_day | 8 | Working hours per day |
| under_utilization_threshold | 70 | % below which team is under-utilized |
| overrun_warning_threshold | 20 | % above which overrun is critical |
| default_core_support_hours | 5 | Hours for core support work |

## Implementation Notes

1. **Calculation Order**: Important to process in correct order to maintain data relationships
2. **Rounding**: Hours are rounded to nearest whole number (except when 0, then set to 1)
3. **Team Context**: Many calculations depend on team context - always pass team name
4. **Sprint Context**: For sprint-specific calculations, filter by iteration/sprint name
5. **Date Ranges**: Week start dates are used consistently for time period calculations
