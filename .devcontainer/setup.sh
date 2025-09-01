#!/bin/bash

# setup.sh - DevContainer post-creation setup script

set -e

echo "🚀 Starting DevContainer setup..."

# Ensure we're in the workspace directory
cd /workspaces/ui-prototyper

# Update system packages
echo "📦 Updating system packages..."
sudo apt update

# Verify multilingual fonts are available (installed via Dockerfile)
echo "🔤 Verifying multilingual font support..."
NOTO_FONTS_COUNT=$(find /usr/share/fonts -name "*Noto*" 2>/dev/null | wc -l)
if [ $NOTO_FONTS_COUNT -gt 0 ]; then
    echo "✅ Found $NOTO_FONTS_COUNT Noto fonts installed for multilingual support"
    echo "   - Hebrew: $(ls /usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf 2>/dev/null && echo "✅" || echo "❌")"
    echo "   - Arabic: $(ls /usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf 2>/dev/null && echo "✅" || echo "❌")"
    echo "   - Armenian: $(ls /usr/share/fonts/truetype/noto/NotoSansArmenian-Regular.ttf 2>/dev/null && echo "✅" || echo "❌")"
    echo "   - Bengali: $(ls /usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf 2>/dev/null && echo "✅" || echo "❌")"
    echo "   - Georgian: $(ls /usr/share/fonts/truetype/noto/NotoSansGeorgian-Regular.ttf 2>/dev/null && echo "✅" || echo "❌")"
    echo "   - CJK: $(ls /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc 2>/dev/null && echo "✅" || echo "❌")"
    echo "   - Devanagari: $(ls /usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf 2>/dev/null && echo "✅" || echo "❌")"
else
    echo "⚠️ Noto fonts not found - multilingual wordcloud may not work properly"
fi

# Install Azure CLI
echo "☁️ Installing Azure CLI..."
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
echo "✅ Azure CLI installed successfully"

# Check Python version (should be installed via devcontainer features)
echo "🐍 Checking Python installation..."
python3 --version
which python3

# Create symbolic link for convenience
if [ ! -f /usr/local/bin/python ]; then
    sudo ln -sf $(which python3) /usr/local/bin/python
fi

# Create and activate Python virtual environment
echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip in virtual environment
echo "⬆️ Upgrading pip in virtual environment..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
if [ -f "api-python/requirements.txt" ]; then
    pip install -r api-python/requirements.txt
    echo "✅ Python dependencies installed from api-python/requirements.txt"
else
    echo "⚠️ No api-python/requirements.txt found, skipping Python dependency installation"
fi

# Install Node.js dependencies for frontend
echo "🎨 Installing Node.js dependencies..."
if [ -f "package.json" ]; then
    npm install
    echo "✅ Node.js dependencies installed from package.json"
else
    echo "⚠️ No package.json found, skipping Node.js dependency installation"
fi

# Set up environment file template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env template..."
    cat > .env << 'EOF'
# Azure AI Configuration
PROJECT_ENDPOINT=https://your-project.services.ai.azure.com
MODEL_DEPLOYMENT_NAME=gpt-4.1

# Development Settings
DEBUG=true
ENVIRONMENT=development
EOF
    echo "✅ Created .env template - please update with your Azure AI configuration"
fi

# Create a simple start script for development
echo "🛠️ Creating development start script..."
cat > start-dev.sh << 'EOF'
#!/bin/bash
# Start development servers

set -e

echo "🚀 Starting development environment..."

# Activate Python virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Python virtual environment activated"
fi

# Start the FastAPI backend in background
echo "🐍 Starting FastAPI backend..."
cd /workspaces/ui-prototyper/api-python
uvicorn main:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 2

# Start the Next.js frontend
echo "⚛️ Starting Next.js frontend..."
cd /workspaces/ui-prototyper
npm run dev &
FRONTEND_PID=$!

echo "🎉 Development servers started!"
echo "📱 Frontend: http://localhost:3000"
echo "�� Backend API: http://localhost:8001"
echo "📖 API Documentation: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for Ctrl+C
trap 'kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
EOF

chmod +x start-dev.sh

echo "�� DevContainer setup complete!"
echo ""
echo "🚀 To get started:"
echo "  1. Update .env with your Azure AI configuration"
echo "  2. Run './start-dev.sh' to start both frontend and backend"
echo "  3. Visit http://localhost:3000 for the frontend"
echo "  4. Visit http://localhost:8001/docs for API documentation"
echo ""
echo "📚 Available commands:"
echo "  - './start-dev.sh' - Start development servers"
echo "  - 'source venv/bin/activate' - Activate Python environment"
echo "  - 'python --version' - Check Python version"
echo "  - 'npm run dev' - Start Next.js development server"
echo "  - 'uvicorn main:app --reload' - Start FastAPI server manually"
echo "  - 'az login' - Login to Azure CLI"
echo "  - 'az --version' - Check Azure CLI version"
