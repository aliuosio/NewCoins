#!/bin/bash


cd ~/projects/Crypto

docker compose up -d

echo "Sleep for 30sec"
sleep 30

docker compose exec python python /src/PumpAndDump/main.py
