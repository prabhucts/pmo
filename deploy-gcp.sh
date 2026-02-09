#!/bin/bash
# Deploy PMO Operations Solution to GCP (pmo-project-2026)
# Uses Artifact Registry (not deprecated Container Registry / gcr.io)
# Usage: OPENAI_API_KEY=xxx SECRET_KEY=xxx ./deploy-gcp.sh

set -e
PROJECT="${GCP_PROJECT:-pmo-project-2026}"
REGION="${GCP_REGION:-us-central1}"
AR_REGISTRY="${REGION}-docker.pkg.dev/${PROJECT}/pmo"

if [ -z "$OPENAI_API_KEY" ]; then
  echo "Warning: OPENAI_API_KEY not set. Set it for AI chat to work."
fi
if [ -z "$SECRET_KEY" ]; then
  export SECRET_KEY="$(openssl rand -hex 32 2>/dev/null || echo 'change-me-in-production')"
  echo "Using generated SECRET_KEY (set SECRET_KEY for production)."
fi

# Ensure Artifact Registry repo exists
gcloud artifacts repositories describe pmo --location="$REGION" 2>/dev/null || \
  gcloud artifacts repositories create pmo \
    --repository-format=docker \
    --location="$REGION" \
    --description="PMO containers"

echo "=== Building and deploying backend ==="
gcloud builds submit --tag "${AR_REGISTRY}/pmo-backend:latest" ./backend

gcloud run deploy pmo-backend \
  --image "${AR_REGISTRY}/pmo-backend:latest" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY},SECRET_KEY=${SECRET_KEY},ALLOWED_ORIGINS=*" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300

BACKEND_URL=$(gcloud run services describe pmo-backend --region "$REGION" --format 'value(status.url)')
API_URL="${BACKEND_URL}/api"
echo "Backend URL: $BACKEND_URL"
echo "API URL (for frontend): $API_URL"

echo "=== Building frontend with REACT_APP_API_URL=$API_URL ==="
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
cd frontend
docker build --build-arg "REACT_APP_API_URL=$API_URL" -t "${AR_REGISTRY}/pmo-frontend:latest" .
docker push "${AR_REGISTRY}/pmo-frontend:latest"
cd ..

echo "=== Deploying frontend ==="
gcloud run deploy pmo-frontend \
  --image "${AR_REGISTRY}/pmo-frontend:latest" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1

FRONTEND_URL=$(gcloud run services describe pmo-frontend --region "$REGION" --format 'value(status.url)')
echo ""
echo "=== Deployment complete ==="
echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL:  $BACKEND_URL"
echo ""
echo "To use custom domain pmo-mng-tool.com:"
echo "  1. Cloud Run → pmo-frontend → Manage custom domains"
echo "  2. Add mapping for pmo-mng-tool.com"
echo "  3. Update DNS per the instructions shown"
