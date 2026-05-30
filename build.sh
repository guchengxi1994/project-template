#!/bin/bash

set -e

VERSION=${1:-latest}
REGISTRY=${REGISTRY:-""}

docker build --platform linux/amd64 -t project-template-backend:$VERSION ./backend
docker build --platform linux/amd64 -t project-template-frontend:$VERSION ./frontend

if [ -n "$REGISTRY" ]; then
    docker tag project-template-backend:$VERSION $REGISTRY/project-template-backend:$VERSION
    docker tag project-template-frontend:$VERSION $REGISTRY/project-template-frontend:$VERSION
    docker push $REGISTRY/project-template-backend:$VERSION
    docker push $REGISTRY/project-template-frontend:$VERSION
fi
