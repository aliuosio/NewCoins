#!/bin/bash

# Navigate to the PumpAndDump project directory
cd "$(dirname "$0")"

# Start Docker Compose in detached mode
docker compose up -d

# Wait 30 seconds for containers to be ready
sleep 30

# Run the scheduler inside the python container
docker compose exec python python -m Scheduler.main
