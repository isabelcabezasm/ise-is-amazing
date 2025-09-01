# You Are Amazing! - FastAPI Python Backend

A modern Python FastAPI backend for the "You Are Amazing!" collaborative message collection application with comprehensive multilingual wordcloud support. **Now deployed in production on Azure Container Apps!**

## 🌐 **Production Deployment**

**Live API**: https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io
**Interactive Docs**: https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/docs
**Health Check**: https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/health

## 🚀 Quick Start

### Local Development

1. **Navigate to the API directory**:

```bash
cd api-python
```

2. **Start the development server**:

```bash
./start-dev.sh
```

3. **Access the API**:
   - API Base URL: `http://localhost:8000`
   - Interactive Documentation: `http://localhost:8000/docs`
   - Alternative Docs: `http://localhost:8000/redoc`

### Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API Endpoints

### Core Message Management

| Method   | Endpoint                      | Description                                       |
| -------- | ----------------------------- | ------------------------------------------------- |
| `GET`    | `/api/amazing`                | Get all amazing messages                          |
| `POST`   | `/api/amazing`                | Create new message or increment reps              |
| `POST`   | `/api/amazing/batch-enhanced` | Process multiple messages with language detection |
| `DELETE` | `/api/amazing`                | Clear all messages (admin only)                   |

### 🌍 Multilingual Word Cloud Endpoints

| Method | Endpoint               | Description                                |
| ------ | ---------------------- | ------------------------------------------ |
| `POST` | `/api/cloud/sentences` | Generate custom multilingual word clouds   |
| `GET`  | `/api/cloud/amazing`   | Generate word cloud from existing messages |

### System Endpoints

| Method | Endpoint  | Description                                |
| ------ | --------- | ------------------------------------------ |
| `GET`  | `/health` | Health check with item count               |
| `GET`  | `/docs`   | Interactive API documentation (Swagger UI) |
| `GET`  | `/redoc`  | Alternative API documentation              |
| `GET`  | `/`       | API info and version                       |

### 🎨 Multilingual Word Cloud Features

**Supported Scripts:**

- Hebrew (עברית), Arabic (العربية), Greek (Ελληνικά)
- Cyrillic (Русский), Armenian (Հայերեն), Bengali (বাংলা)
- Georgian (ქართული), CJK (中文, 日本語, 한국어)
- Devanagari (हिन्दी), Latin (English, Español, Français, etc.)

**Production Font Support:**

- 2,380+ Noto fonts deployed in Azure Container Apps
- Automatic script detection and font selection
- Mixed-language sentence rendering support

### Interactive Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔧 API Usage Examples

### Message Management

```bash
# Get all messages
curl -X GET "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/amazing"

# Add new message
curl -X POST "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/amazing" \
  -H "Content-Type: application/json" \
  -d '{"text": "Tu es formidable!", "language": "French"}'

# Health check
curl -X GET "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/health"
```

### 🌍 Multilingual Word Cloud Examples

```bash
# Generate mixed language word cloud
curl -X POST "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/cloud/sentences" \
  -H "Content-Type: application/json" \
  -d '{
    "sentences": [
      "שלום עולם, זה טקסט בעברית",
      "Hello world, this is English text",
      "مرحبا بالعالم، هذا نص باللغة العربية"
    ],
    "width": 800,
    "height": 600,
    "background_color": "white",
    "colormap": "viridis"
  }' --output multilingual_wordcloud.png

# Generate word cloud from existing messages
curl -X GET "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/cloud/amazing?width=800&height=400" \
  --output amazing_wordcloud.png
```

## 📋 Data Models

### AmazingItem

```python
{
  "id": "string",
  "text": "string",
  "language": "string",
  "reps": 1
}
```

### Create Request

```python
{
  "text": "string",
  "language": "string"  # Optional, defaults to "English"
}
```

## 🌟 Features

- **🌍 Comprehensive Multilingual Support**: 10+ world scripts with proper font rendering
- **🎨 Advanced Word Cloud Generation**: Custom multilingual wordcloud engine
- **📚 FastAPI Framework**: Modern, fast, and automatic API documentation
- **⚡ Production Ready**: Deployed on Azure Container Apps with 2,380+ fonts
- **🔍 Auto Language Detection**: Intelligent script detection for proper rendering
- **🎯 CORS Enabled**: Works with any frontend application
- **📊 Duplicate Detection**: Increments `reps` for duplicate messages
- **🛡️ Type Safety**: Full Pydantic model validation
- **📖 Auto Documentation**: Interactive Swagger UI and ReDoc
- **💚 Health Checks**: Built-in health monitoring with metrics
- **🔄 Development Ready**: Hot reload during development

## 🐳 Production Deployment (Azure Container Apps)

The API is deployed using Azure Container Apps with comprehensive font support:

**Container Configuration:**

- **Base Image**: Python 3.11-slim
- **Fonts**: Complete Noto font family (2,380+ fonts)
- **Memory**: 0.5Gi per container instance
- **Auto-scaling**: 0-3 replicas based on demand
- **Health Monitoring**: Built-in health checks

**Azure Resources:**

- **Container Registry**: youareamazingacr1756051313.azurecr.io
- **Container App**: youareamazing-api (West US 2)
- **Environment**: youareamazing-env with managed certificates

## 🐳 Docker Support

### Build Docker Image

```bash
docker build -t youareamazing-api .
```

### Run with Docker

```bash
docker run -p 8000:8000 youareamazing-api
```

## 🔄 Comparison with JavaScript Version

| Feature       | JavaScript (Azure Functions) | Python (FastAPI)         |
| ------------- | ---------------------------- | ------------------------ |
| Framework     | Azure Functions              | FastAPI                  |
| Language      | JavaScript/Node.js           | Python                   |
| Documentation | Manual                       | Auto-generated           |
| Development   | Azure-specific               | Standard Python          |
| Local Testing | Azure Functions Core Tools   | Standard Python server   |
| Type Safety   | Basic                        | Full Pydantic validation |
| CORS          | Manual setup                 | Middleware               |

## 🚀 Deployment Options

### 🌟 Current Production (Azure Container Apps)

**Status**: ✅ **Currently Deployed and Running**

```bash
# Production API
curl https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/health

# Deploy updates to existing API
cd /workspaces/ui-prototyper && ./deployment/update-python-api.sh
```

### 🐳 Local Docker Development

```bash
# Build local Docker image
docker build -t youareamazing-api .

# Run with Docker (includes all multilingual fonts)
docker run -p 8000:8000 youareamazing-api
```

### ☁️ Alternative Azure Deployment Options

#### 1. New Azure Container Apps Deployment

```bash
# Deploy to new Container Apps instance (creates new URL)
./deployment/deploy-python-api.sh
```

#### 2. Azure App Service

```bash
# Deploy to Azure App Service from Container Registry
az webapp create \
  --resource-group rg-youareamazing-python \
  --plan myplan \
  --name youareamazing-api-appservice \
  --deployment-container-image-name youareamazingacr1756051313.azurecr.io/youareamazing-api:latest
```

## 🛠️ Development

### Project Structure

```
api-python/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── start-dev.sh        # Development server script
└── README.md           # This file
```

### Adding New Features

1. Add new endpoints in `main.py`
2. Define Pydantic models for request/response validation
3. Test using the interactive documentation at `/docs`

## 🔧 Configuration

Environment variables (optional):

- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)
- `DEBUG`: Enable debug mode (default: False)

## 📝 License

This project is part of the "You Are Amazing!" application suite.

---

**Remember: You are amazing! 🌟**
