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
