#!/bin/bash

IMAGE="123567901111/knowspace:latest"
APP_DIR="/home/ayushi/KnowSpace"
LOGFILE="/var/log/knowspace-docker.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" >> "$LOGFILE"
}

cd "$APP_DIR" || { log "Directory $APP_DIR not found!"; exit 1; }

log "Checking for image updates..."

CURRENT_DIGEST=$(docker image inspect "$IMAGE" --format='{{index .RepoDigests 0}}' 2>/dev/null)

docker pull "$IMAGE" >> "$LOGFILE" 2>&1

NEW_DIGEST=$(docker image inspect "$IMAGE" --format='{{index .RepoDigests 0}}' 2>/dev/null)

if [ "$CURRENT_DIGEST" != "$NEW_DIGEST" ]; then
    log "New image found. Restarting containers..."
    docker-compose down >> "$LOGFILE" 2>&1
    docker-compose up -d >> "$LOGFILE" 2>&1
    log "Containers restarted."
else
    log "No new image found. Will retry in 5 minutes."
fi