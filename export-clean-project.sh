#!/bin/bash

# Script to export the current project without git history
# This creates a clean copy that can be added to another repository

set -e

# Get the current directory name as default export name
CURRENT_DIR=$(basename "$(pwd)")
EXPORT_DIR="./export/${CURRENT_DIR}-clean"

# Allow custom export directory as first argument
if [ $# -eq 1 ]; then
    EXPORT_DIR="$1"
fi

echo "🚀 Exporting clean project to: $EXPORT_DIR"

# Remove existing export directory if it exists
if [ -d "$EXPORT_DIR" ]; then
    echo "📁 Removing existing export directory..."
    rm -rf "$EXPORT_DIR"
fi

# Create export directory
mkdir -p "$EXPORT_DIR"

echo "📋 Copying project files..."

# Copy all files except those we want to exclude
rsync -av --progress \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='.next' \
    --exclude='out' \
    --exclude='build' \
    --exclude='coverage' \
    --exclude='*.log' \
    --exclude='.DS_Store' \
    --exclude='*.pem' \
    --exclude='.env*' \
    --exclude='.vercel' \
    --exclude='*.tsbuildinfo' \
    --exclude='__pycache__' \
    --exclude='api-python/__pycache__' \
    --exclude='api-python/venv' \
    --exclude='venv' \
    --exclude='api-python/*.png' \
    --exclude='api-python/server.log' \
    --exclude='api-python/*.ini' \
    --exclude='export' \
    . "$EXPORT_DIR"/

echo "🧹 Cleaning up temporary files..."

# Remove any remaining cache directories
find "$EXPORT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$EXPORT_DIR" -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true
find "$EXPORT_DIR" -name ".next" -type d -exec rm -rf {} + 2>/dev/null || true

echo "📊 Project structure:"
cd "$EXPORT_DIR"
tree -L 2 -I 'node_modules|__pycache__|.next' || ls -la

echo ""
echo "✅ Clean project exported successfully!"
echo "📁 Location: $EXPORT_DIR"
echo ""
echo "🔧 Next steps:"
echo "1. Navigate to the exported directory: cd '$EXPORT_DIR'"
echo "2. Option A - Create new repository:"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial commit'"
echo ""
echo "3. Option B - Add to existing repository:"
echo "   - Copy contents to your target repository"
echo "   - Or use: cp -r '$EXPORT_DIR'/* /path/to/your/target/repo/"
echo ""
echo "4. Don't forget to install dependencies:"
echo "   npm install"
echo "   cd api-python && pip install -r requirements.txt"
