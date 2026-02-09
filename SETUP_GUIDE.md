# PMO Operations Solution - Setup Guide

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Edit .env and add your OpenAI API key
# DATABASE_URL=sqlite:///./pmo.db
# OPENAI_API_KEY=your-key-here

# Run the backend
python -m uvicorn app.main:app --reload
```

The backend will be available at http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env.local

# Start development server
npm start
```

The frontend will be available at http://localhost:3000

## Using Your Data

### 1. Prepare Your Files

Place your data files in the `data/` directory (or use the web UI):

- **rally_userstories.csv** - Export from Rally with columns:
  - Formatted ID, Name, Owner, Parent, Portfolio Item, Feature, Project, Release, Iteration, Plan Estimate

- **rally_features.csv** - Export from Rally with columns:
  - Formatted ID, Name, Owner, Parent, Project, Release

- **rally_epics.csv** - Export from Rally with columns:
  - Formatted ID, Name, State, Project, Owner, Parent

- **clarity_timesheet.csv** - Export from Clarity with columns:
  - Team, Initiative, Resource Name (in Clarity), Network ID or email Location, Location, and weekly date columns

### 2. Upload Data via Web UI

1. Navigate to http://localhost:3000/upload
2. Upload each file type:
   - User Stories
   - Features
   - Epics
   - Clarity Timesheet

### 3. Configure Business Rules

1. Navigate to http://localhost:3000/rules
2. Add/Edit rules:
   - Story Point to Hours conversion (default: 13 hours)
   - Sprint duration (default: 2 weeks)
   - Working hours per day (default: 8)
   - Team allocation percentages

Example rule configuration:
```json
{
  "name": "story_point_hours",
  "rule_type": "conversion",
  "parameters": {
    "value": 13,
    "unit": "hours"
  },
  "is_active": true,
  "priority": 10
}
```

### 4. Generate Insights

1. Navigate to http://localhost:3000/insights
2. Click "Generate New Insights"
3. View generated insights for:
   - Project overruns
   - Team under-utilization
   - Forecast alerts

### 5. Use AI Chat

1. Navigate to http://localhost:3000/chat
2. Ask questions like:
   - "Show me projects with overruns this sprint"
   - "Which teams are under-utilized?"
   - "Forecast completion for ITPR082135"
   - "Who hasn't entered hours this week?"

## Business Logic from VBA

The application implements the following business logic extracted from your VBA modules:

### 1. Story Point Conversion
- 1 Story Point = 13 hours (configurable per team)
- Applied to all user stories and defects

### 2. Team Allocation
- Reads team member allocation percentages from Team Members sheet
- Calculates rally allocation percentage per team
- Distributes effort across team members

### 3. Clarity Allocation Calculation
- Calculates per-week hours based on story points
- Factors in team size and allocation percentages
- Handles core support hours for non-feature work

### 4. Defect Tracking
- Links defects to features or user stories
- Adds defect estimates to feature totals
- Tracks L3 defects separately

### 5. Sprint Calendar
- Maps sprints to week start/end dates
- 10 working days per sprint (2 weeks)
- Tracks sprint progress and velocity

### 6. Insights Generation

**Project Overruns:**
- Compares planned hours (from Clarity allocations) vs actual hours (from time entries)
- Flags when actual > planned by any percentage
- Severity: warning if < 20%, critical if >= 20%

**Under-Utilization:**
- Calculates available hours per team member (8 hours/day * 5 days * allocation %)
- Compares allocated hours to available hours
- Flags teams under 70% utilization

**Forecasting:**
- Calculates remaining story points
- Computes average velocity from last 3 sprints
- Estimates remaining sprints and completion date
- Identifies risks (low velocity, high remaining work, etc.)

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Troubleshooting

### Backend Issues

**Database errors:**
```bash
# Reset database
rm pmo.db
# Restart backend to recreate tables
```

**Import errors:**
```bash
# Ensure you're in the backend directory and venv is activated
pip install -r requirements.txt
```

### Frontend Issues

**API connection errors:**
- Check that backend is running on port 8000
- Verify .env.local has correct API URL
- Check browser console for CORS errors

**Build errors:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Production Deployment

### Backend

1. Use PostgreSQL instead of SQLite:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ```

2. Set proper environment variables:
   ```
   DEBUG=False
   SECRET_KEY=<generate-strong-key>
   ```

3. Use a production WSGI server:
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend

1. Build for production:
   ```bash
   npm run build
   ```

2. Serve with nginx or similar:
   ```nginx
   server {
     listen 80;
     server_name yourdomain.com;
     
     location / {
       root /path/to/build;
       try_files $uri /index.html;
     }
     
     location /api {
       proxy_pass http://backend:8000;
     }
   }
   ```

## Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review API documentation at /api/docs
3. Check console errors in browser developer tools
