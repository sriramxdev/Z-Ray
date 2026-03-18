#!/bin/bash
# Z-Ray Standalone Docker Launcher

echo "🚀 Preparing Z-Ray Docker Deployment..."
cd "$(dirname "$0")"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "❌ Error: Docker is not running. Please start Docker and try again."
  exit 1
fi

echo "📦 Building and Starting Containers..."
docker-compose up --build -d

echo ""
echo "✨ Z-Ray is now deploying!"
echo "🔗 Access the platform at: http://localhost:5000"
echo "📝 Logs can be viewed with: docker-compose logs -f"
echo ""
echo "To stop the platform, run: docker-compose down"
