#!/bin/bash
# KGAS Production Deployment Script
# TD.5 Production Deployment Implementation

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-kgas-production}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
KUBECONFIG="${KUBECONFIG:-}"
DRY_RUN="${DRY_RUN:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check docker
    if ! command -v docker &> /dev/null; then
        log_error "docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check kubernetes cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create namespace if it doesn't exist
create_namespace() {
    log_info "Creating namespace: $NAMESPACE"
    
    if kubectl get namespace "$NAMESPACE" &> /dev/null; then
        log_warning "Namespace $NAMESPACE already exists"
    else
        kubectl create namespace "$NAMESPACE"
        log_success "Namespace $NAMESPACE created"
    fi
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building and pushing Docker image..."
    
    local image_name="kgas:${IMAGE_TAG}"
    local registry_image="registry.example.com/kgas:${IMAGE_TAG}"
    
    # Build image
    log_info "Building image: $image_name"
    docker build -t "$image_name" -f docker/Dockerfile .
    
    # Tag for registry
    docker tag "$image_name" "$registry_image"
    
    # Push to registry (uncomment for real deployment)
    # log_info "Pushing image: $registry_image"
    # docker push "$registry_image"
    
    log_success "Docker image built and tagged"
}

# Validate Kubernetes manifests
validate_manifests() {
    log_info "Validating Kubernetes manifests..."
    
    local manifests=(
        "k8s/secrets.yaml"
        "k8s/deployment.yaml"
        "k8s/service.yaml"
        "k8s/monitoring.yaml"
        "k8s/backup-cronjob.yaml"
    )
    
    for manifest in "${manifests[@]}"; do
        if [[ ! -f "$manifest" ]]; then
            log_error "Manifest file not found: $manifest"
            exit 1
        fi
        
        # Validate syntax
        if ! kubectl apply --dry-run=client -f "$manifest" &> /dev/null; then
            log_error "Invalid manifest: $manifest"
            exit 1
        fi
    done
    
    log_success "All manifests validated"
}

# Deploy secrets and configmaps
deploy_config() {
    log_info "Deploying configuration..."
    
    local apply_cmd="kubectl apply -n $NAMESPACE"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        apply_cmd="$apply_cmd --dry-run=server"
        log_info "DRY RUN: Would deploy configuration"
    fi
    
    # Apply secrets first
    $apply_cmd -f k8s/secrets.yaml
    log_success "Secrets deployed"
}

# Deploy application
deploy_application() {
    log_info "Deploying KGAS application..."
    
    local apply_cmd="kubectl apply -n $NAMESPACE"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        apply_cmd="$apply_cmd --dry-run=server"
        log_info "DRY RUN: Would deploy application"
    fi
    
    # Deploy in order
    $apply_cmd -f k8s/deployment.yaml
    $apply_cmd -f k8s/service.yaml
    
    log_success "Application deployed"
}

# Deploy monitoring
deploy_monitoring() {
    log_info "Deploying monitoring..."
    
    local apply_cmd="kubectl apply -n $NAMESPACE"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        apply_cmd="$apply_cmd --dry-run=server"
        log_info "DRY RUN: Would deploy monitoring"
    fi
    
    $apply_cmd -f k8s/monitoring.yaml
    log_success "Monitoring deployed"
}

# Deploy backup system
deploy_backup() {
    log_info "Deploying backup system..."
    
    local apply_cmd="kubectl apply -n $NAMESPACE"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        apply_cmd="$apply_cmd --dry-run=server"
        log_info "DRY RUN: Would deploy backup system"
    fi
    
    $apply_cmd -f k8s/backup-cronjob.yaml
    log_success "Backup system deployed"
}

# Wait for deployment to be ready
wait_for_deployment() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would wait for deployment to be ready"
        return
    fi
    
    log_info "Waiting for deployment to be ready..."
    
    if kubectl wait --for=condition=available --timeout=300s deployment/kgas-api -n "$NAMESPACE"; then
        log_success "Deployment is ready"
    else
        log_error "Deployment failed to become ready within timeout"
        exit 1
    fi
}

# Verify deployment
verify_deployment() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY RUN: Would verify deployment"
        return
    fi
    
    log_info "Verifying deployment..."
    
    # Check pods
    local pod_count
    pod_count=$(kubectl get pods -n "$NAMESPACE" -l app=kgas-api --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [[ "$pod_count" -gt 0 ]]; then
        log_success "$pod_count KGAS pods running"
    else
        log_error "No KGAS pods running"
        exit 1
    fi
    
    # Check services
    if kubectl get service kgas-service -n "$NAMESPACE" &> /dev/null; then
        log_success "KGAS service is available"
    else
        log_error "KGAS service not found"
        exit 1
    fi
    
    # Test health endpoint
    local pod_name
    pod_name=$(kubectl get pods -n "$NAMESPACE" -l app=kgas-api --field-selector=status.phase=Running -o jsonpath='{.items[0].metadata.name}')
    
    if [[ -n "$pod_name" ]]; then
        if kubectl exec "$pod_name" -n "$NAMESPACE" -- curl -f http://localhost:8000/health &> /dev/null; then
            log_success "Health endpoint responding"
        else
            log_warning "Health endpoint not responding"
        fi
    fi
}

# Rollback deployment
rollback_deployment() {
    log_warning "Rolling back deployment..."
    
    kubectl rollout undo deployment/kgas-api -n "$NAMESPACE"
    kubectl rollout status deployment/kgas-api -n "$NAMESPACE"
    
    log_success "Deployment rolled back"
}

# Clean up deployment
cleanup_deployment() {
    log_info "Cleaning up deployment..."
    
    kubectl delete -f k8s/ -n "$NAMESPACE" --ignore-not-found=true
    
    log_success "Deployment cleaned up"
}

# Show deployment status
show_status() {
    log_info "Deployment Status:"
    echo "===================="
    
    echo -e "\n${BLUE}Pods:${NC}"
    kubectl get pods -n "$NAMESPACE" -l app=kgas-api
    
    echo -e "\n${BLUE}Services:${NC}"
    kubectl get services -n "$NAMESPACE"
    
    echo -e "\n${BLUE}Ingress:${NC}"
    kubectl get ingress -n "$NAMESPACE"
    
    echo -e "\n${BLUE}Deployments:${NC}"
    kubectl get deployments -n "$NAMESPACE"
    
    echo -e "\n${BLUE}Recent Events:${NC}"
    kubectl get events -n "$NAMESPACE" --sort-by='.lastTimestamp' | tail -10
}

# Main deployment function
main() {
    log_info "Starting KGAS Production Deployment"
    log_info "Namespace: $NAMESPACE"
    log_info "Image Tag: $IMAGE_TAG"
    log_info "Dry Run: $DRY_RUN"
    
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            create_namespace
            validate_manifests
            build_and_push_image
            deploy_config
            deploy_application
            deploy_monitoring
            deploy_backup
            wait_for_deployment
            verify_deployment
            show_status
            log_success "KGAS Production Deployment Complete!"
            ;;
        "status")
            show_status
            ;;
        "rollback")
            rollback_deployment
            ;;
        "cleanup")
            cleanup_deployment
            ;;
        "validate")
            validate_manifests
            log_success "All manifests are valid"
            ;;
        *)
            echo "Usage: $0 {deploy|status|rollback|cleanup|validate}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Full deployment (default)"
            echo "  status   - Show deployment status"
            echo "  rollback - Rollback to previous version"
            echo "  cleanup  - Remove all resources"
            echo "  validate - Validate manifests only"
            echo ""
            echo "Environment Variables:"
            echo "  NAMESPACE  - Kubernetes namespace (default: kgas-production)"
            echo "  IMAGE_TAG  - Docker image tag (default: latest)"
            echo "  DRY_RUN    - Set to 'true' for dry run (default: false)"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"