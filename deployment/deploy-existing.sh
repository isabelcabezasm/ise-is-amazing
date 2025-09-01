#!/bin/bash

# Azure Static Web Apps Deployment Script for existing "You are amazing!" App with Python API
# This script deploys the frontend to existing Azure Static Web App

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🚀 Deploying Frontend to Existing Azure Static Web App${NC}"
echo -e "${BLUE}=============================================${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed. Please install npm first.${NC}"
    exit 1
fi

if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ package.json not found. Please run this script from your project root.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"

# Install Azure Static Web Apps CLI if not present
if ! command_exists swa; then
    echo -e "${BLUE}📦 Installing Azure Static Web Apps CLI...${NC}"
    npm install -g @azure/static-web-apps-cli
fi

# Update API configuration for production
echo -e "${BLUE}⚙️ Updating API configuration for production...${NC}"
cat > lib/api-config.ts << 'EOF'
// API configuration for different environments
const getApiBaseUrl = () => {
  // In development, use the local Python API
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000';
  }
  
  // In production, use the deployed Python API
  // Update this URL with your actual Python API deployment
  return 'https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io';
};

export const API_BASE_URL = getApiBaseUrl();
export const AMAZING_API_URL = `${API_BASE_URL}/api/amazing`;
EOF

# Build the application
echo -e "${BLUE}🔨 Building application...${NC}"
npm install
npm run build

echo -e "${GREEN}✅ Build completed successfully${NC}"

# Check if build output exists
if [ ! -d "out" ]; then
    echo -e "${RED}❌ Build output directory 'out' not found${NC}"
    exit 1
fi

echo -e "${BLUE}📁 Build output contains:${NC}"
ls -la out/

# Azure deployment token - you'll need to set this
DEPLOYMENT_TOKEN="${AZURE_STATIC_WEB_APPS_API_TOKEN}"

if [ -z "$DEPLOYMENT_TOKEN" ]; then
    echo -e "${YELLOW}⚠️  AZURE_STATIC_WEB_APPS_API_TOKEN environment variable not set${NC}"
    echo -e "${BLUE}Please set your deployment token:${NC}"
    echo "1. Go to Azure Portal"
    echo "2. Navigate to your Static Web App"
    echo "3. Click 'Manage deployment token'"
    echo "4. Copy the token"
    echo "5. Run: export AZURE_STATIC_WEB_APPS_API_TOKEN='your-token-here'"
    echo ""
    read -p "Enter your deployment token now: " DEPLOYMENT_TOKEN
    
    if [ -z "$DEPLOYMENT_TOKEN" ]; then
        echo -e "${RED}❌ No deployment token provided${NC}"
        exit 1
    fi
fi

# Deploy using SWA CLI (frontend only, no API)
echo -e "${BLUE}🚀 Deploying frontend to Azure Static Web Apps...${NC}"
echo "Deploying from: $(pwd)/out"

npx @azure/static-web-apps-cli deploy \
    --deployment-token "$DEPLOYMENT_TOKEN" \
    --app-location "out" \
    --output-location "" \
    --verbose

echo -e "${BLUE}⏳ Waiting for deployment to propagate...${NC}"
sleep 30

# Test the deployment
APP_URL="https://white-cliff-0303bcc1e-preview.westus2.2.azurestaticapps.net"
echo -e "${BLUE}🧪 Testing deployment...${NC}"

if curl -f "$APP_URL" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ App is responding at $APP_URL${NC}"
else
    echo -e "${YELLOW}⚠️ App might still be starting up${NC}"
fi

# Test the cloud page specifically
if curl -f "$APP_URL/cloud" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Cloud page is accessible at $APP_URL/cloud${NC}"
else
    echo -e "${YELLOW}⚠️ Cloud page might still be deploying${NC}"
fi

echo -e "${GREEN}🎉 Frontend deployment completed!${NC}"
echo -e "${PURPLE}================================${NC}"
echo -e "${GREEN}Your 'You are amazing!' frontend has been updated!${NC}"
echo ""
echo -e "${BLUE}📱 Frontend URLs:${NC}"
echo "  Main App: $APP_URL/amazing"
echo "  Cloud Page: $APP_URL/cloud"
echo "  Admin Panel: $APP_URL/delete"
echo ""
echo -e "${YELLOW}� Python API Status:${NC}"
echo "  The frontend now expects the Python API to be deployed separately"
echo "  Configure your Python API URL in lib/api-config.ts"
echo ""
echo -e "${BLUE}� To deploy the Python API:${NC}"
echo "  1. cd api-python"
echo "  2. Build Docker image: docker build -t youareamazing-api ."
echo "  3. Deploy to Azure Container Apps or Container Instances"
echo "  4. Update the API URL in lib/api-config.ts"
echo ""
echo -e "${GREEN}✨ Your app is ready with modern Python backend!${NC}"
