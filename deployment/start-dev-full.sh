#!/bin/bash

echo "🚀 Starting You Are Amazing! Development Environment"
echo "=============================================="

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down development servers..."
    kill $PYTHON_PID 2>/dev/null
    kill $NEXTJS_PID 2>/dev/null
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Start Python FastAPI server
echo "1️⃣ Starting Python FastAPI server..."
cd api-python
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    venv/bin/pip install -r requirements.txt
fi

venv/bin/uvicorn main:app --host 0.0.0.0 --port 8002 --reload &
PYTHON_PID=$!
cd ..

# Wait for Python API to start
echo "⏳ Waiting for Python API to start..."
sleep 3

# Test if Python API is responding
if curl -s http://localhost:8002/ > /dev/null; then
    echo "✅ Python API is running on http://localhost:8002"
    echo "📚 API Documentation: http://localhost:8002/docs"
else
    echo "❌ Python API failed to start"
    kill $PYTHON_PID 2>/dev/null
    exit 1
fi

# Start Next.js development server
echo ""
echo "2️⃣ Starting Next.js frontend..."
npm run dev &
NEXTJS_PID=$!

# Wait for Next.js to start
echo "⏳ Waiting for Next.js to start..."
sleep 5

echo ""
echo "🎉 Development environment is ready!"
echo "================================================"
echo "📱 Frontend: http://localhost:3000"
echo "🐍 Python API: http://localhost:8002"
echo "📚 API Docs: http://localhost:8002/docs"
echo "================================================"
echo ""
echo "🔗 Quick Links:"
echo "   • Amazing App: http://localhost:3000/amazing"
echo "   • Cloud View:  http://localhost:3000/cloud"
echo "   • Admin Panel: http://localhost:3000/delete"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for user to interrupt
wait
