#!/bin/bash

# Stop and remove any running containers
docker compose down -v

# Build and start all services in detached mode
docker compose up --build -d

# Wait for the services to be ready
sleep 10

# Send a test prompt to the planner service
curl -XPOST http://localhost:8100/plan -d '{"prompt":"Invent a room-temperature superconductor"}' -H "Content-Type: application/json"