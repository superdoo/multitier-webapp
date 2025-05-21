#!/bin/bash

# Namespaces to delete
namespaces=("mt-backend" "mt-frontend" "mt-database")

echo "Deleting Minikube namespaces..."

for ns in "${namespaces[@]}"; do
    echo "Deleting namespace: $ns"
    kubectl delete namespace "$ns"
done

echo "All specified namespaces have been deleted."
