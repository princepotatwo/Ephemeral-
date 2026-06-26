#!/bin/bash
# Game Server Launcher — run from Terminal: bash start_server.sh
# Starts the local game server AND the ngrok tunnel for public access.

cd "$(dirname "$0")"

# -----------------------
# 1. Check dependencies
# -----------------------
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "ERROR: Python is not installed or not in PATH!"
    echo "Please install Python from https://www.python.org/downloads/"
    exit 1
fi

if ! command -v ngrok &>/dev/null; then
    echo "ERROR: ngrok is not installed or not in PATH!"
    echo "Please install ngrok from https://ngrok.com/download"
    exit 1
fi

# -----------------------
# 2. Stop any existing local server on port 8000
# -----------------------
OLD_SERVER=$(lsof -ti :8000 2>/dev/null)
if [ -n "$OLD_SERVER" ]; then
    echo "Stopping existing server on port 8000..."
    kill $OLD_SERVER 2>/dev/null
    sleep 1
fi

# -----------------------
# 3. Stop any existing ngrok tunnel for this domain
# -----------------------
OLD_NGROK=$(pgrep -f "ngrok http --url https://backless-watch-recovery.ngrok-free.dev")
if [ -n "$OLD_NGROK" ]; then
    echo "Stopping existing ngrok tunnel..."
    kill $OLD_NGROK 2>/dev/null
    sleep 2
fi

# -----------------------
# 4. Start local server
# -----------------------
echo "Starting local server on port 8000..."
$PY_CMD server.py &
SERVER_PID=$!

# Cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# Wait for server to be ready
echo "Waiting for server to start..."
for i in {1..10}; do
    if curl -s -o /dev/null http://localhost:8000; then
        echo "Server ready!"
        break
    fi
    sleep 1
done

# -----------------------
# 5. Start ngrok tunnel
# -----------------------
echo ""
echo "Starting ngrok tunnel..."
echo "Public URL: https://backless-watch-recovery.ngrok-free.dev/index.html"
echo "(This link works from anywhere — phone, friend's house, etc.)"
echo ""

ngrok http --url https://backless-watch-recovery.ngrok-free.dev 8000
