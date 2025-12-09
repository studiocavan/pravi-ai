#!/bin/bash

# Script to create frontend ConfigMap from files
# This needs to be run before deploying the frontend

echo "Creating frontend ConfigMap from frontend/ directory..."

kubectl create configmap frontend-files \
  --from-file=../frontend/ \
  --namespace=pravi-ai \
  --dry-run=client -o yaml | kubectl apply -f -

if [ $? -eq 0 ]; then
    echo "✓ Frontend ConfigMap created successfully"
else
    echo "✗ Failed to create frontend ConfigMap"
    exit 1
fi
