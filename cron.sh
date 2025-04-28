#!/bin/bash

# Navigate to the PumpAndDump project directory
cd "$(dirname "$0")"

# Start Docker Compose in detached mode
docker compose up -d

printf "\rContainers should be ready!                   \n"

# Run the scheduler inside the python container
docker compose exec python python Scheduler/main.py
