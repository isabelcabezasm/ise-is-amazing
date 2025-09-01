#!/bin/bash

# Deploy Python FastAPI to Azure Container Apps
# This script creates and deploys the Python API backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🐍 Deploying Python FastAPI to Azure${NC}"
echo -e "${BLUE}=====================================${NC}"

# Configuration
RESOURCE_GROUP="rg-youareamazing-python"
LOCATION="westus2"
CONTAINER_ENV_NAME="youareamazing-env"
CONTAINER_APP_NAME="youareamazing-api"
ACR_NAME="youareamazingacr$(date +%s)"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if ! command_exists az; then
    echo -e "${RED}❌ Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if [ ! -f "api-python/main.py" ]; then
    echo -e "${RED}❌ Python API not found. Please run this from project root.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"

# Login to Azure
echo -e "${BLUE}🔐 Checking Azure login status...${NC}"
if ! az account show &> /dev/null; then
    echo "Please login to Azure:"
    az login
fi

# Create resource group
echo -e "${BLUE}📁 Creating resource group...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

# Create Azure Container Registry
echo -e "${BLUE}📦 Creating Azure Container Registry...${NC}"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Basic \
    --admin-enabled true \
    --output none

# Get ACR login server
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query "loginServer" --output tsv)
echo -e "${GREEN}✅ Registry created: $ACR_LOGIN_SERVER${NC}"

# Build and push Docker image
echo -e "${BLUE}🔨 Building and pushing Docker image...${NC}"
cd api-python

# Build the Docker image
docker build -t $ACR_LOGIN_SERVER/youareamazing-api:latest .

# Login to ACR and push
az acr login --name $ACR_NAME
docker push $ACR_LOGIN_SERVER/youareamazing-api:latest

cd ..

echo -e "${GREEN}✅ Image pushed successfully${NC}"

# Create Container Apps environment
echo -e "${BLUE}🌐 Creating Container Apps environment...${NC}"
az containerapp env create \
    --name $CONTAINER_ENV_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --output none

# Create the container app
echo -e "${BLUE}🚀 Creating Container App...${NC}"
az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_ENV_NAME \
    --image $ACR_LOGIN_SERVER/youareamazing-api:latest \
    --target-port 8000 \
    --ingress 'external' \
    --registry-server $ACR_LOGIN_SERVER \
    --registry-username $ACR_NAME \
    --registry-password $(az acr credential show --name $ACR_NAME --query "passwords[0].value" --output tsv) \
    --cpu 0.25 \
    --memory 0.5Gi \
    --min-replicas 0 \
    --max-replicas 1 \
    --output none

# Get the app URL
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" \
    --output tsv)

echo ""
echo -e "${GREEN}🎉 Python API deployment completed!${NC}"
echo -e "${PURPLE}====================================${NC}"
echo ""
echo -e "${BLUE}📱 API Information:${NC}"
echo "  API URL: https://$APP_URL"
echo "  Health Check: https://$APP_URL/health"
echo "  Amazing API: https://$APP_URL/api/amazing"
echo "  Documentation: https://$APP_URL/docs"
echo ""
echo -e "${BLUE}📝 Azure Resources:${NC}"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Container Registry: $ACR_NAME"
echo "  Container App: $CONTAINER_APP_NAME"
echo ""
echo -e "${YELLOW}🔧 Next Steps:${NC}"
echo "1. Update lib/api-config.ts with the new API URL:"
echo "   return 'https://$APP_URL';"
echo ""
echo "2. Redeploy your frontend:"
echo "   ./deploy-existing.sh"
echo ""
echo "3. Test the API:"
echo "   curl https://$APP_URL/api/amazing"
echo ""
echo -e "${GREEN}✨ Your Python API is now live on Azure!${NC}"
