# Stop main app
echo "[MAIN] Stopping container"
docker ps --filter status=running --filter name=ia24-assigments-bot -q | xargs docker stop

# Delete main app container
echo "[MAIN] Removing container"
docker ps --filter status=exited --filter name=ia24-assigments-bot -q | xargs docker rm

# Delete main image
echo "[MAIN] Removing image"
docker image rm ia24-assigments-bot --force

# Begin building main image
echo "[MAIN] Building image"
docker compose up

# Start main container
echo "[MAIN] Starting container"
python3 run.py -d