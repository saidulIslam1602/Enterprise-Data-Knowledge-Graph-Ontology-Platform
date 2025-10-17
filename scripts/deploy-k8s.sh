#!/bin/bash

# Enterprise Knowledge Graph Platform - Kubernetes Deployment Script
# This script deploys the platform to a Kubernetes cluster

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="knowledge-graph"
K8S_DIR="./k8s"
TIMEOUT="300s"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Enterprise Knowledge Graph Platform${NC}"
echo -e "${GREEN}Kubernetes Deployment Script${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    echo "Please check your kubeconfig and cluster access"
    exit 1
fi

echo -e "${GREEN}✓ kubectl installed and cluster accessible${NC}\n"

# Get current context
CURRENT_CONTEXT=$(kubectl config current-context)
echo -e "${YELLOW}Current Kubernetes context: ${CURRENT_CONTEXT}${NC}"
read -p "Continue with this context? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

echo -e "\n${GREEN}Step 1: Creating namespace...${NC}"
kubectl apply -f ${K8S_DIR}/namespace.yaml
echo -e "${GREEN}✓ Namespace created/updated${NC}\n"

echo -e "${GREEN}Step 2: Deploying ConfigMaps and Secrets...${NC}"
kubectl apply -f ${K8S_DIR}/configmap.yaml
kubectl apply -f ${K8S_DIR}/secrets.yaml
echo -e "${GREEN}✓ ConfigMaps and Secrets deployed${NC}\n"

echo -e "${GREEN}Step 3: Deploying storage (PVCs)...${NC}"
kubectl apply -f ${K8S_DIR}/fuseki-deployment.yaml -n ${NAMESPACE}
kubectl apply -f ${K8S_DIR}/postgres-deployment.yaml -n ${NAMESPACE}
kubectl apply -f ${K8S_DIR}/redis-deployment.yaml -n ${NAMESPACE}
echo -e "${GREEN}✓ Storage deployed${NC}\n"

echo -e "${GREEN}Step 4: Deploying backend services...${NC}"
kubectl apply -f ${K8S_DIR}/api-deployment.yaml -n ${NAMESPACE}
echo -e "${GREEN}✓ API server deployed${NC}\n"

echo -e "${GREEN}Step 5: Deploying frontend...${NC}"
kubectl apply -f ${K8S_DIR}/dashboard-deployment.yaml -n ${NAMESPACE}
echo -e "${GREEN}✓ Dashboard deployed${NC}\n"

echo -e "${GREEN}Step 6: Deploying ingress...${NC}"
kubectl apply -f ${K8S_DIR}/ingress.yaml -n ${NAMESPACE}
echo -e "${GREEN}✓ Ingress configured${NC}\n"

echo -e "${GREEN}Step 7: Waiting for deployments to be ready...${NC}"
echo "This may take a few minutes..."

# Wait for deployments
kubectl wait --for=condition=available --timeout=${TIMEOUT} deployment/fuseki -n ${NAMESPACE} || true
kubectl wait --for=condition=available --timeout=${TIMEOUT} deployment/postgres -n ${NAMESPACE} || true
kubectl wait --for=condition=available --timeout=${TIMEOUT} deployment/redis -n ${NAMESPACE} || true
kubectl wait --for=condition=available --timeout=${TIMEOUT} deployment/api -n ${NAMESPACE} || true
kubectl wait --for=condition=available --timeout=${TIMEOUT} deployment/dashboard -n ${NAMESPACE} || true

echo -e "\n${GREEN}Step 8: Checking deployment status...${NC}"
kubectl get pods -n ${NAMESPACE}
echo

# Get service endpoints
echo -e "${GREEN}Step 9: Getting service endpoints...${NC}"
echo -e "\nServices:"
kubectl get svc -n ${NAMESPACE}

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Get ingress information
INGRESS_IP=$(kubectl get ingress knowledge-graph-ingress -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
if [ "$INGRESS_IP" != "pending" ] && [ -n "$INGRESS_IP" ]; then
    echo -e "${GREEN}Access your platform at:${NC}"
    echo -e "  Dashboard: http://${INGRESS_IP}"
    echo -e "  API: http://${INGRESS_IP}:8000"
    echo -e "  Fuseki: http://${INGRESS_IP}:3030"
else
    echo -e "${YELLOW}Ingress IP is pending. Check status with:${NC}"
    echo -e "  kubectl get ingress -n ${NAMESPACE}"
fi

echo -e "\n${GREEN}Useful commands:${NC}"
echo -e "  View logs: kubectl logs -f deployment/<service-name> -n ${NAMESPACE}"
echo -e "  Scale: kubectl scale deployment/<service-name> --replicas=<n> -n ${NAMESPACE}"
echo -e "  Delete: kubectl delete namespace ${NAMESPACE}"
echo -e "  Port forward: kubectl port-forward svc/<service-name> <local-port>:<service-port> -n ${NAMESPACE}"

echo -e "\n${GREEN}Done! 🚀${NC}"
