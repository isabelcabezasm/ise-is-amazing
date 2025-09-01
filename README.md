# You Are Amazing! 🌟

A multilingual collaborative message collection application that spreads positivity worldwide. Built with Next.js, Python FastAPI, and deployed on Azure with comprehensive multilingual wordcloud support.

## ✨ Features

- **🌍 Multilingual Support**: Full support for 10+ world scripts including Hebrew, Arabic, Greek, CJK, Armenian, Bengali, Georgian, and more
- **🎨 Multilingual Word Clouds**: Generate beautiful word clouds that render mixed languages correctly
- **☁️ Azure Deployment**: Production-ready deployment on Azure Static Web Apps + Container Apps
- **⚡ Real-time Collaboration**: Multiple users can add and view items simultaneously
- **🎯 Modern UI**: Built with shadcn/ui components and Tailwind CSS
- **📱 Mobile Responsive**: Works perfectly on all devices
- **🔐 Admin Panel**: Secure admin interface for content management

## 🚀 Quick Start

### Local Development

1. **Clone and Install**:

```bash
git clone https://github.com/isabelcabezasm/youareamazing.git
cd youareamazing
npm install
```

2. **Start Full Development Environment**:

```bash
./deployment/start-dev-full.sh
```

This starts both the Next.js frontend and Python FastAPI backend.

3. **Visit the Applications**:
   - **Frontend**: `http://localhost:3000`
   - **API Documentation**: `http://localhost:8000/docs`
   - **Amazing App**: `http://localhost:3000/amazing`
   - **Word Clouds**: `http://localhost:3000/cloud`

## 🚀 Deploy to Azure

We provide easy deployment scripts for Azure:

### Frontend Deployment

```bash
# First-time deployment (creates new resources)
./deployment/deploy-azure-dynamic.sh

# Subsequent deployments (updates existing resources)
./deployment/deploy-existing.sh
```

### Backend API Deployment

```bash
# First-time API deployment (creates new Container Apps resources)
./deployment/deploy-python-api.sh

# Update existing API (preserves URL)
./deployment/update-python-api.sh
```

## 🌍 Multilingual Support

### Supported Scripts & Languages

- **Hebrew** (עברית) - Right-to-left text support
- **Arabic** (العربية) - Full Arabic script support
- **Greek** (Ελληνικά) - Ancient and modern Greek
- **Cyrillic** (Русский, Български, etc.) - Russian, Bulgarian, Serbian
- **Armenian** (Հայերեն) - Complete Armenian script
- **Bengali** (বাংলা) - Bengali and related scripts
- **Georgian** (ქართული) - Georgian script support
- **CJK Scripts** (中文, 日本語, 한국어) - Chinese, Japanese, Korean
- **Devanagari** (हिन्दी, संस्कृतम्) - Hindi, Sanskrit, and related
- **Latin Scripts** (English, Español, Français, Deutsch, Italiano, etc.)

### Font Infrastructure

- **Production Fonts**: Comprehensive Noto font collection (2,380+ fonts)
- **DevContainer Fonts**: Automated font installation for development
- **Smart Font Detection**: Automatic script detection and font selection
- **Mixed Language Support**: Render multiple languages in single word clouds

## 🛠️ Tech Stack

- **Frontend**: Next.js 15+ with App Router
- **Backend**: Python FastAPI with comprehensive multilingual support
- **UI Library**: shadcn/ui components
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Deployment**: Azure Static Web Apps + Azure Container Apps
- **Fonts**: Complete Noto font family for multilingual support
- **Word Clouds**: Custom multilingual wordcloud library
- **API Documentation**: Auto-generated Swagger UI

## 📁 Project Structure

```
app/
├── amazing/           # Main "You are amazing!" message collection
├── cloud/             # Multilingual word cloud generation interface
├── delete/            # Admin panel with authentication
└── globals.css        # Global styles with Tailwind

api-python/
├── main.py                           # FastAPI application
├── multilingual_wordcloud_sentences.py  # Custom multilingual wordcloud engine
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Production container config
└── README.md                        # API documentation

components/
└── ui/                # shadcn/ui component library

deployment/
├── deploy-azure-dynamic.sh    # First-time frontend deployment
├── deploy-existing.sh         # Update existing frontend
├── deploy-python-api.sh       # First-time API deployment
├── update-python-api.sh       # Update existing API
└── start-dev-full.sh         # Full development environment

lib/
├── api-config.ts      # API endpoint configuration
└── utils.ts           # Utility functions
```

## 🎯 Application Pages

### 1. Amazing Messages (`/amazing`)

- **Purpose**: Collect multilingual "You are amazing" messages
- **Features**: Auto-language detection, duplicate handling, real-time updates
- **API**: POST/GET `/api/amazing`

### 2. Word Cloud Generator (`/cloud`)

- **Purpose**: Generate beautiful multilingual word clouds
- **Features**: Mixed language support, customizable styling, downloadable images
- **API**: POST `/api/cloud/sentences`, GET `/api/cloud/amazing`

### 3. Admin Panel (`/delete`)

- **Purpose**: Administrative management of messages
- **Features**: Secure authentication, bulk delete operations
- **Credentials**: `NEXT_PUBLIC_ADMIN_USERNAME` / `NEXT_PUBLIC_ADMIN_PASSWORD`

## 🔧 API Endpoints

### Message Management

| Method   | Endpoint                      | Description                   |
| -------- | ----------------------------- | ----------------------------- |
| `GET`    | `/api/amazing`                | Retrieve all messages         |
| `POST`   | `/api/amazing`                | Add message or increment reps |
| `DELETE` | `/api/amazing`                | Clear all messages            |
| `POST`   | `/api/amazing/batch-enhanced` | Batch message processing      |

### Word Cloud Generation

| Method | Endpoint               | Description                                |
| ------ | ---------------------- | ------------------------------------------ |
| `POST` | `/api/cloud/sentences` | Generate custom sentence word clouds       |
| `GET`  | `/api/cloud/amazing`   | Generate word cloud from existing messages |

### System

| Method | Endpoint  | Description                   |
| ------ | --------- | ----------------------------- |
| `GET`  | `/health` | API health check              |
| `GET`  | `/docs`   | Interactive API documentation |

## 🌟 Multilingual Word Cloud Features

### Custom MultilingualWordCloud Engine

- **Script Detection**: Automatic detection of Hebrew, Arabic, CJK, Latin, and more
- **Font Mapping**: Smart font selection per script for proper rendering
- **Mixed Language**: Handle sentences with multiple scripts simultaneously
- **Production Ready**: Deployed with 2,380+ Noto fonts in Azure Container Apps

### API Usage Examples

**Generate Mixed Language Word Cloud:**

```bash
curl -X POST "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/api/cloud/sentences" \
  -H "Content-Type: application/json" \
  -d '{
    "sentences": [
      "שלום עולם, זה טקסט בעברית",
      "Hello world, this is English text",
      "مرحبا بالعالم، هذا نص باللغة العربية",
      "Γεια σας κόσμε, αυτό είναι ελληνικό κείμενο"
    ],
    "width": 800,
    "height": 600,
    "background_color": "white",
    "colormap": "viridis"
  }' --output multilingual_wordcloud.png
```

## 💝 Philosophy

This application embodies the belief that **you are amazing** in every language. Whether you're collecting positive messages from around the world or creating beautiful multilingual word clouds, every interaction celebrates the diversity and beauty of human expression.

## 🌟 Environment Configuration

### Required Environment Variables

```bash
# Admin authentication (optional, defaults provided)
NEXT_PUBLIC_ADMIN_USERNAME=admin
NEXT_PUBLIC_ADMIN_PASSWORD=amazing_password_123
```

### Development vs Production

- **Development**: Automatically uses `http://localhost:8000` for API
- **Production**: Uses deployed Azure Container Apps API endpoint

## 🤝 Contributing

We welcome contributions that:

- Enhance multilingual support for new scripts/languages
- Improve word cloud generation algorithms
- Add new positive messaging features
- Strengthen Azure deployment processes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Remember: You are amazing in every language! �✨**

```

**Optional:** Enable 'auto approve' in Copilot settings to automatically apply agent-written changes to the codebase. You'll still be able to review and choose whether to keep or discard changes from the entire session. This setting can be found in VS Code settings > Chat > Tools > Auto Approve.


## Example

See the simple prompt in the GitHub Copilot chat, and the web preview that was generated.
<img width="1768" alt="Screenshot 2025-06-04 at 11 39 10 AM" src="https://github.com/user-attachments/assets/d783e75a-477c-4298-87c9-e13284cf5b3e" />
```
