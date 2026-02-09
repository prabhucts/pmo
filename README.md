# PMO Operations Solution

An AI-powered PMO operations platform for IT teams and projects with insights, forecasting, and reconciliation capabilities.

## Features

- **AI Chat Interface**: Natural language queries for project insights
- **Configurable Rules Engine**: UI-based business rule configuration
- **Data Integration**: Rally (User Stories, Features, EPICs) + Clarity (Timesheet)
- **Insights & Analytics**:
  - Project overruns detection
  - Under-utilization analysis
  - Team hour tracking
  - Individual/team forecasting by project
  - Sprint-wise reconciliation
  - Alerts and notifications

## Architecture

- **Backend**: Python FastAPI
- **Frontend**: React + TypeScript
- **Database**: PostgreSQL
- **AI/LLM**: OpenAI GPT-4 with LangChain
- **Data Processing**: Pandas, NumPy

## Business Logic

### Key Conversions
- 1 Story Point = 13 hours (configurable)
- Sprint = 10 working days (2 weeks)
- Weekly allocation tracking

### Data Mappings
- User Story → Feature → Epic → ITPR (Project)
- Team Members → Projects → Weekly Hours
- Defects → Features/User Stories → Effort

### Insights
1. **Project Ended but Allocation Exists**: Detect when projects are completed but Clarity still has allocations
2. **Project Overruns**: Actual hours > planned hours
3. **Under-utilization**: Allocated hours < available capacity
4. **Team Hour Entry**: Track who's entering hours vs not
5. **Forecasting**: Predict completion based on velocity and remaining work

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure your settings
python -m alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Environment Variables
Create a `.env` file in the backend directory:
```
DATABASE_URL=postgresql://user:password@localhost:5432/pmo_db
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key_here
```

## Usage

1. **Upload Data**: Import Rally exports and Clarity timesheets
2. **Configure Rules**: Set up story point conversions, sprint calendars, and business rules
3. **Chat Interface**: Ask questions like:
   - "Show me projects with overruns this sprint"
   - "Which team members haven't entered hours this week?"
   - "Forecast completion date for Project ITPR082135"
   - "Show under-utilized teams this PI"
4. **View Dashboards**: Real-time insights and analytics

## API Documentation

Once running, visit:
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000

## Data Files & Templates

- **Sample data**: The app seeds the database with sample data on first run (from `backend/templates/`).
- **Templates**: Use the **Templates** page in the UI to download CSV templates (Rally epics, features, user stories, Clarity timesheet). Upload your data via the **Upload Data** page.

Place custom data in `data/` or upload via the UI:
- `rally_userstories.csv` - User Stories extract
- `rally_features.csv` - Features extract
- `rally_epics.csv` - EPICs extract
- `clarity_timesheet.csv` - Clarity allocations

## Repository & Deployment

- **GitHub repo**: [pmo_project](https://github.com/YOUR_USERNAME/pmo_project) – push this codebase to a new repo named `pmo_project`.
- **GCP deployment**: Deploy to Google Cloud project **pmo-project-2026** (Cloud Run). Custom domain: **https://pmo-mng-tool.com** for the UI.
- See **[DEPLOYMENT.md](DEPLOYMENT.md)** for:
  - Creating the GitHub repository
  - GCP project setup and Cloud Run deploy
  - Mapping the custom domain **pmo-mng-tool.com** to the frontend service
  - Environment variables and optional CI/CD (GitHub Actions)

Quick deploy (from project root):
```bash
OPENAI_API_KEY=xxx SECRET_KEY=xxx ./deploy-gcp.sh
```

## License

MIT
