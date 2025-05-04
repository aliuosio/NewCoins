#!/bin/bash
cd "$(dirname "$0")"
docker compose up -d
docker compose exec python python Scheduler/main.py
