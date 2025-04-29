# Nimble Challenge Deployment Guide

## Prerequisites
- Install [Docker](https://docs.docker.com/engine/install/ubuntu/)
- Install [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- Install [Minikube](https://minikube.sigs.k8s.io/docs/start/?arch=%2Flinux%2Fx86-64%2Fstable%2Fbinary+download)


## 1. Build Docker Image inside Minikube

```bash
minikube start --driver=docker
```
```bash
eval $(minikube docker-env)
docker build -t nimble-challenge-server:latest .
```

## 2. Apply Kubernetes Deployment and Service

```bash
kubectl apply -f deploy/deployment.yaml
kubectl apply -f deploy/service.yaml
```

## 3. Create a Tunnel (for LoadBalancer IP)

```bash
minikube tunnel
```

## 4. Check if pods running and service port is correct
```bash
kubectl get pods
kubectl get svc my-service
```

## 5. Launch Chrome WebApp:
```bash
MINIKUBE_IP=$(minikube ip)
google-chrome   --enable-quic   --enable-experimental-web-platform-features   --ignore-certificate-errors   --ignore-certificate-errors-spki-list=ggR1vjmsgl5RdfYS3f5C2nYyZ3LRrjfOyD/Va/JLcXQ=   --origin-to-force-quic-on=${MINIKUBE_IP}:30403   https://${MINIKUBE_IP}:30403/
```