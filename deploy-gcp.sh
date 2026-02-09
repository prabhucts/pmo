#!/bin/bash
# Deploy PMO Operations Solution to GCP (pmo-project)
# Usage: OPENAI_API_KEY=xxx SECRET_KEY=xxx ./deploy-gcp.sh
# Optional: BACKEND_URL=https://... to skip backend deploy and only build frontend with that API URL

set -e
PROJECT="${GCP_PROJECT:-pmo-project}"
REGION="${GCP_REGION:-us-central1}"

if [ -z "$OPENAI_API_KEY" ]; then
  echo "Warning: OPENAI_API_KEY not set. Set it for AI chat to work."
fi
if [ -z "$SECRET_KEY" ]; then
  export SECRET_KEY="$(openssl rand -hex 32 2>/dev/null || echo 'change-me-in-production')"
  echo "Using generated SECRET_KEY (set SECRET_KEY for production)."
fi

echo "=== Building and deploying backend ==="
gcloud builds submit --tag "gcr.io/${PROJECT}/pmo-backend" ./backend

gcloud run deploy pmo-backend \
  --image "gcr.io/${PROJECT}/pmo-backend" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY},SECRET_KEY=${SECRET_KEY},ALLOWED_ORIGINS=https://pmo-mng-tool.com,https://localhost:3000" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300

BACKEND_URL=$(gcloud run services describe pmo-backend --region "$REGION" --format 'value(status.url)')
API_URL="${BACKEND_URL}/api"
echo "Backend URL: $BACKEND_URL"
echo "API URL (for frontend): $API_URL"

echo "=== Building frontend with REACT_APP_API_URL=$API_URL ==="
cd frontend
docker build --build-arg "REACT_APP_API_URL=$API_URL" -t "gcr.io/${PROJECT}/pmo-frontend" .
docker push "gcr.io/${PROJECT}/pmo-frontend"
cd ..

echo "=== Deploying frontend ==="
gcloud run deploy pmo-frontend \
  --image "gcr.io/${PROJECT}/pmo-frontend" \
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
