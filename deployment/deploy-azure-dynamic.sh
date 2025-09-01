#!/bin/bash

# Deploy Next.js app with Python FastAPI to Azure
# This version deploys the frontend to Azure Static Web Apps
# and provides instructions for deploying the Python API separately

set -e

echo "🚀 Starting Azure deployment with Python FastAPI backend..."

# Configuration
RESOURCE_GROUP="rg-youareamazing-python"
LOCATION="westus2"
SWA_NAME="youareamazing-python"
CONTAINER_APP_NAME="youareamazing-api"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if SWA CLI is installed
if ! command -v swa &> /dev/null; then
    echo "📦 Installing Azure Static Web Apps CLI..."
    npm install -g @azure/static-web-apps-cli
fi

# Login to Azure (if not already logged in)
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "Please login to Azure:"
    az login
fi

# Create resource group if it doesn't exist
echo "📁 Creating/checking resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

# Create the Static Web App with Free tier (frontend only)
echo "🌐 Creating Azure Static Web App..."
SWA_OUTPUT=$(az staticwebapp create \
    --name $SWA_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Free \
    --output json)

echo "✅ Static Web App created successfully!"
DEFAULT_HOSTNAME=$(echo $SWA_OUTPUT | jq -r '.defaultHostname')
echo "🌍 Frontend will be available at: https://$DEFAULT_HOSTNAME"

# Get deployment token
echo "🔑 Getting deployment token..."
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list --name $SWA_NAME --resource-group $RESOURCE_GROUP --query "properties.apiKey" --output tsv)

# Update the API configuration for production
echo "⚙️ Updating API configuration for production..."
cat > lib/api-config.ts << 'EOF'
// API configuration for different environments
const getApiBaseUrl = () => {
  // In development, use the local Python API
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000';
  }
  
  // In production, use the deployed Python API
  // You'll need to update this URL after deploying the Python API
  return 'https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io';
};

export const API_BASE_URL = getApiBaseUrl();
export const AMAZING_API_URL = `${API_BASE_URL}/api/amazing`;
EOF

# Build the application
echo "🔨 Building Next.js application..."
npm run build

# Deploy using SWA CLI (frontend only)
echo "📤 Deploying frontend to Azure Static Web Apps..."
swa deploy \
    --deployment-token $DEPLOYMENT_TOKEN \
    --app-location . \
    --output-location out \
    --verbose

echo ""
echo "🎉 Frontend deployment completed successfully!"
echo "🌍 Your frontend is now live at: https://$DEFAULT_HOSTNAME"
echo "📝 Resource Group: $RESOURCE_GROUP"
echo "📱 Static Web App: $SWA_NAME"
echo ""
echo "� Next: Deploy the Python API"
echo "================================"
echo "To deploy the Python FastAPI backend, run:"
echo ""
echo "cd api-python"
echo "az containerapp create \\"
echo "  --name $CONTAINER_APP_NAME \\"
echo "  --resource-group $RESOURCE_GROUP \\"
echo "  --environment mycontainerenvironment \\"
echo "  --image python:3.11-slim \\"
echo "  --target-port 8000 \\"
echo "  --ingress 'external'"
echo ""
echo "Or use Azure Container Instances:"
echo "az container create \\"
echo "  --resource-group $RESOURCE_GROUP \\"
echo "  --name $CONTAINER_APP_NAME \\"
echo "  --image youracr.azurecr.io/youareamazing-api \\"
echo "  --ports 8000"
echo ""
echo "🌟 Pages available (once API is deployed):"
echo "   - https://$DEFAULT_HOSTNAME/amazing (main app)"
echo "   - https://$DEFAULT_HOSTNAME/cloud (read-only view)"
echo "   - https://$DEFAULT_HOSTNAME/delete (admin panel)"
echo ""
echo "🔄 To redeploy frontend, just run this script again!"
