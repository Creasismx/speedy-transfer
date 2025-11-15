#!/bin/bash
echo "Starting Daphne server with HTTP and WebSocket support..."
echo ""
cd "$(dirname "$0")"
daphne -b 0.0.0.0 -p 8001 config.asgi:application

