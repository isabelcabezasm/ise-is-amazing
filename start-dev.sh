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
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
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
echo "�� Backend API: http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for Ctrl+C
trap 'kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
