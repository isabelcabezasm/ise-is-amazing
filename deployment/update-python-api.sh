#!/bin/bash

# Update Python FastAPI in existing Azure Container Apps
# This script updates the existing deployment without changing the URL

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🔄 Updating Python FastAPI in Azure${NC}"
echo -e "${BLUE}=====================================${NC}"

# Configuration - using existing resources
RESOURCE_GROUP="rg-youareamazing-python"
CONTAINER_APP_NAME="youareamazing-api"
NEW_IMAGE_TAG="latest-$(date +%s)"

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

# Check if container app exists
echo -e "${BLUE}🔍 Checking existing container app...${NC}"
if ! az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${RED}❌ Container app '$CONTAINER_APP_NAME' not found in resource group '$RESOURCE_GROUP'${NC}"
    echo -e "${YELLOW}💡 Use './deploy-python-api.sh' for initial deployment${NC}"
    exit 1
fi

# Get existing ACR name from the container app
echo -e "${BLUE}🔍 Getting existing registry information...${NC}"
EXISTING_IMAGE=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.template.containers[0].image" \
    --output tsv)

ACR_LOGIN_SERVER=$(echo $EXISTING_IMAGE | cut -d'/' -f1)
ACR_NAME=$(echo $ACR_LOGIN_SERVER | cut -d'.' -f1)

echo -e "${GREEN}✅ Found existing registry: $ACR_LOGIN_SERVER${NC}"

# Build and push new Docker image
echo -e "${BLUE}🔨 Building and pushing updated Docker image...${NC}"
cd api-python

# Build the Docker image with new tag
sudo service docker restart
sleep 3
sudo docker build -t $ACR_LOGIN_SERVER/youareamazing-api:$NEW_IMAGE_TAG .

# Login to ACR and push
az acr login --name $ACR_NAME
sudo docker push $ACR_LOGIN_SERVER/youareamazing-api:$NEW_IMAGE_TAG

cd ..

echo -e "${GREEN}✅ New image pushed successfully${NC}"

# Update the container app with new image
echo -e "${BLUE}🚀 Updating Container App...${NC}"
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --image $ACR_LOGIN_SERVER/youareamazing-api:$NEW_IMAGE_TAG \
    --output none

# Get the app URL (should be the same)
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.configuration.ingress.fqdn" \
    --output tsv)

echo ""
echo -e "${GREEN}🎉 Python API update completed!${NC}"
echo -e "${PURPLE}=================================${NC}"
echo ""
echo -e "${BLUE}📱 API Information (unchanged):${NC}"
echo "  API URL: https://$APP_URL"
echo "  Health Check: https://$APP_URL/health"
echo "  Amazing API: https://$APP_URL/api/amazing"
echo "  Documentation: https://$APP_URL/docs"
echo ""
echo -e "${GREEN}✅ Your updated Python API is live!${NC}"
echo -e "${BLUE}🔄 The URL remains the same - no frontend changes needed.${NC}"
echo ""
echo -e "${YELLOW}🧪 Test the updated API:${NC}"
echo "   curl https://$APP_URL/api/amazing"
