#!/bin/bash

IMAGE="123567901111/knowspace:latest"

echo "📦 Building Docker image..."
docker build -t $IMAGE .

echo "🚀 Pushing to Docker Hub..."
docker push $IMAGE

echo "♻️ Restarting containers..."
docker-compose down
docker-compose pull
docker-compose up -d

echo "✅ Done!"
