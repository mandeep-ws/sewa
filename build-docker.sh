#!/bin/bash

# Build script for Docker deployment
echo "🐳 Building SEWA Book Automation System Docker Image..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "🚀 To start the application:"
    echo "   docker-compose up -d"
    echo ""
    echo "🌐 Access at: http://localhost:8501"
    echo ""
    echo "📁 Data files will be available in the current directory:"
    echo "   - All_Sent_Records.xlsx"
    echo "   - Duplicate_Transactions.xlsx"
    echo "   - Failed_Transactions.xlsx"
    echo "   - exports/ (validation results)"
    echo "   - uploads/ (uploaded files)"
else
    echo "❌ Docker build failed. Please check the error messages above."
    exit 1
fi
