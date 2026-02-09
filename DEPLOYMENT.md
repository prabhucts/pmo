# PMO Operations Solution – Deployment Guide

This guide covers deploying the PMO application to **Google Cloud Platform (GCP)** project **pmo-project**, with the UI served at **https://pmo-mng-tool.com**.

---

## 1. GitHub Repository (pmo_project)

### Create the repository

1. On GitHub: **New repository** → Name: `pmo_project` → Create (no README).
2. Locally, from the project root:

```bash
cd /Users/prabhu/Documents/pmo

# Add all files (respects .gitignore)
git add .
git commit -m "Initial commit: PMO Operations Solution with GCP deployment"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/pmo_project.git
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME` with your GitHub username or org.

---

## 2. GCP Project Setup (pmo-project)

### Enable APIs and set project

```bash
# Install gcloud CLI if needed: https://cloud.google.com/sdk/docs/install

# Login and set project
gcloud auth login
gcloud config set project pmo-project

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sqladmin.googleapis.com   # if using Cloud SQL later
```

### (Optional) Service account for GitHub Actions

```bash
# Create a service account for CI/CD
gcloud iam service-accounts create pmo-deploy \
  --display-name "PMO Deploy"

# Grant roles
gcloud projects add-iam-policy-binding pmo-project \
  --member="serviceAccount:pmo-deploy@pmo-project.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding pmo-project \
  --member="serviceAccount:pmo-deploy@pmo-project.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding pmo-project \
  --member="serviceAccount:pmo-deploy@pmo-project.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create key and save as GitHub secret GCP_SA_KEY (base64 or JSON content)
gcloud iam service-accounts keys create key.json \
  --iam-account=pmo-deploy@pmo-project.iam.gserviceaccount.com
# Add key content as GitHub secret: GCP_SA_KEY (and optionally OPENAI_API_KEY, SECRET_KEY)
```

---

## 3. Build and Deploy to Cloud Run

### Backend

Build and deploy from the **repository root** (so `backend/` is the build context):

```bash
cd /Users/prabhu/Documents/pmo

# Build backend image
gcloud builds submit --tag gcr.io/pmo-project/pmo-backend ./backend

# Deploy to Cloud Run
gcloud run deploy pmo-backend \
  --image gcr.io/pmo-project/pmo-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=your-openai-key,SECRET_KEY=your-secret-key,ALLOWED_ORIGINS=https://pmo-mng-tool.com" \
  --memory 2Gi \
  --cpu 2
```

Note the **backend URL** from the deploy output (e.g. `https://pmo-backend-xxxxx-uc.a.run.app`). You will use this for the frontend and for the custom domain.

### Frontend

Frontend must call the backend API. Set `REACT_APP_API_URL` to the backend base URL including `/api` (e.g. `https://pmo-backend-xxxxx-uc.a.run.app/api`).

**Option A – Build with Cloud Build (recommended)**

Create `frontend/cloudbuild.yaml` or build with inline substitution:

```bash
cd /Users/prabhu/Documents/pmo

# Replace BACKEND_URL with your actual backend URL (including /api)
export BACKEND_URL="https://pmo-backend-xxxxx-uc.a.run.app/api"

gcloud builds submit ./frontend \
  --config=frontend/cloudbuild-frontend.yaml
```

Create `frontend/cloudbuild-frontend.yaml`:

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '--build-arg'
      - 'REACT_APP_API_URL=${_BACKEND_URL}'
      - '-t'
      - 'gcr.io/$PROJECT_ID/pmo-frontend:latest'
      - '.'
substitutions:
  _BACKEND_URL: 'https://pmo-backend-xxxxx-uc.a.run.app/api'
```

Then deploy:

```bash
gcloud run deploy pmo-frontend \
  --image gcr.io/pmo-project/pmo-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Option B – Local Docker build**

```bash
cd frontend
docker build --build-arg REACT_APP_API_URL=https://pmo-backend-xxxxx-uc.a.run.app/api -t gcr.io/pmo-project/pmo-frontend .
docker push gcr.io/pmo-project/pmo-frontend
gcloud run deploy pmo-frontend --image gcr.io/pmo-project/pmo-frontend --platform managed --region us-central1 --allow-unauthenticated
```

---

## 4. Custom Domain: pmo-mng-tool.com

You want the **UI** at **https://pmo-mng-tool.com**. That is the frontend. The backend can stay on its default Cloud Run URL or you can add a subdomain (e.g. `api.pmo-mng-tool.com`) later.

### Map domain to frontend (Cloud Run)

1. **Verify domain ownership** (if not already):
   - [Google Webmaster Central](https://www.google.com/webmasters/verification/home) or
   - Cloud Console → APIs & Services → Domain verification.

2. **Map the domain to the frontend service**:
   - Cloud Console → **Cloud Run** → select **pmo-frontend** → **Manage custom domains**.
   - **Add mapping** → **Verify** your domain (e.g. `pmo-mng-tool.com`).
   - Add mapping: **pmo-mng-tool.com** (and optionally **www.pmo-mng-tool.com**) to the **pmo-frontend** service.

3. **DNS (at your registrar)**  
   Cloud Run will show the required records (usually a CNAME or A/AAAA). Example:
   - **CNAME** `pmo-mng-tool.com` → `ghs.google.com` or the target Cloud Run gives you (e.g. `ghs.googlehosted.com` or the Cloud Run domain).
   - For Cloud Run, the UI often gives a **custom domain** like `pmo-frontend-xxxxx.run.app`; then:
     - **CNAME** `pmo-mng-tool.com` → that hostname, or
     - Use the exact target shown in “Manage custom domains”.

4. **SSL**  
   Cloud Run provisions TLS automatically for mapped domains.

### Optional: API subdomain

To use **https://api.pmo-mng-tool.com** for the backend:

- In Cloud Run → **pmo-backend** → **Manage custom domains** → add **api.pmo-mng-tool.com**.
- In DNS: **CNAME** `api.pmo-mng-tool.com` → the target shown for pmo-backend.
- Rebuild the frontend with `REACT_APP_API_URL=https://api.pmo-mng-tool.com/api` and redeploy.

---

## 5. Default Data and Templates

- **Default data**: On first startup, the backend seeds the database with sample data from `backend/templates/` if the database is empty (see `app/services/seed_data.py`).
- **Templates**: The UI has a **Templates** page that lists and downloads CSV templates from the backend (`/api/templates/list`, `/api/templates/download/{id}`). Template files live in `backend/templates/` and are included in the backend image.

No extra step is required for “load current data by default” or template downloads beyond deploying the backend as above.

---

## 6. Environment Variables Summary

| Variable | Backend | Frontend (build-time) | Notes |
|----------|---------|------------------------|--------|
| `OPENAI_API_KEY` | ✅ | - | For AI chat |
| `SECRET_KEY` | ✅ | - | App secret |
| `ALLOWED_ORIGINS` | ✅ | - | e.g. `https://pmo-mng-tool.com` |
| `DATABASE_URL` | ✅ | - | Omit for default SQLite in container; for production use Cloud SQL or similar |
| `REACT_APP_API_URL` | - | ✅ | Backend base URL + `/api`, e.g. `https://pmo-backend-xxx.run.app/api` |

---

## 7. Quick Deploy Script (from repo root)

Save as `deploy-gcp.sh` and run from the project root:

```bash
#!/bin/bash
set -e
PROJECT=pmo-project
REGION=us-central1

echo "Building backend..."
gcloud builds submit --tag gcr.io/${PROJECT}/pmo-backend ./backend

echo "Deploying backend..."
gcloud run deploy pmo-backend \
  --image gcr.io/${PROJECT}/pmo-backend \
  --platform managed --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY},SECRET_KEY=${SECRET_KEY},ALLOWED_ORIGINS=https://pmo-mng-tool.com" \
  --memory 2Gi --cpu 2

BACKEND_URL=$(gcloud run services describe pmo-backend --region ${REGION} --format 'value(status.url)')
echo "Backend URL: ${BACKEND_URL}"

echo "Building frontend with API URL: ${BACKEND_URL}/api"
cd frontend
docker build --build-arg REACT_APP_API_URL=${BACKEND_URL}/api -t gcr.io/${PROJECT}/pmo-frontend .
docker push gcr.io/${PROJECT}/pmo-frontend
cd ..

echo "Deploying frontend..."
gcloud run deploy pmo-frontend \
  --image gcr.io/${PROJECT}/pmo-frontend \
  --platform managed --region ${REGION} \
  --allow-unauthenticated

echo "Done. Map pmo-mng-tool.com to pmo-frontend in Cloud Run → Manage custom domains."
```

Run: `OPENAI_API_KEY=... SECRET_KEY=... ./deploy-gcp.sh`

---

## 8. Checklist

- [ ] GitHub repo `pmo_project` created and code pushed
- [ ] GCP project `pmo-project` set and APIs enabled
- [ ] Backend built and deployed to Cloud Run; URL noted
- [ ] Frontend built with `REACT_APP_API_URL=<backend-url>/api` and deployed to Cloud Run
- [ ] Domain **pmo-mng-tool.com** verified and mapped to **pmo-frontend** in Cloud Run
- [ ] DNS CNAME (or A) for pmo-mng-tool.com pointing to Cloud Run
- [ ] GitHub secrets set if using GitHub Actions (GCP_SA_KEY, OPENAI_API_KEY, SECRET_KEY)

After deployment, open **https://pmo-mng-tool.com** to use the PMO Management Tool. Sample data is loaded by default; users can download templates from the Templates page and upload their own data.
