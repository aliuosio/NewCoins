#!/bin/bash

# Navigate to the PumpAndDump project directory
cd "$(dirname "$0")"

# Start Docker Compose in detached mode
docker compose up -d

# Wait 30 seconds for containers to be ready (countdown)
for i in {40..1}; do
  printf "\rWaiting for Python Dependencies to load: %2d seconds remaining..." "$i"
  sleep 1
done
printf "\rContainers should be ready!                   \n"

# Run the scheduler inside the python container
docker compose exec python python -m Scheduler.main
