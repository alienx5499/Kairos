# Incident Root Cause Analysis and Troubleshooting Guide

This guide documents two common Kubernetes production failure modes prepared for the Kairos platform, with the diagnosis steps and reproduction commands.

## Scenario 1: ImagePullBackOff outage

### 1. Failure description and manifest
File: `troubleshooting/broken-image.yaml`

The deployment requests container image `ghcr.io/prabalpatra/kairos-backend:v999.0.0-nonexistent`. Because this tag does not exist in the container registry, the kubelet fails to fetch the image layers.

### 2. Diagnosis steps
When applying this manifest:
```bash
kubectl apply -f troubleshooting/broken-image.yaml
```

Inspect the pod status in the namespace:
```bash
kubectl get pods -n kairos -l app=kairos-broken-image
```

Expected output:
```text
NAME                                   READY   STATUS             RESTARTS   AGE
kairos-broken-image-78df6f9b48-x9kz2   0/1     ImagePullBackOff   0          45s
```

Run `describe` on the pod to inspect events:
```bash
kubectl describe pod kairos-broken-image-78df6f9b48-x9kz2 -n kairos
```

The events table shows:
```text
Events:
  Type     Reason     Age                From               Message
  ----     ------     ----               ----               -------
  Normal   Scheduled  60s                default-scheduler  Successfully assigned kairos/kairos-broken-image-78df6f9b48-x9kz2 to ip-10-0-10-42
  Normal   Pulling    15s (x3 over 58s)  kubelet            Pulling image "ghcr.io/prabalpatra/kairos-backend:v999.0.0-nonexistent"
  Warning  Failed     14s (x3 over 57s)  kubelet            Failed to pull image "ghcr.io/prabalpatra/kairos-backend:v999.0.0-nonexistent": rpc error: code = NotFound desc = failed to pull and unpack image: not found
  Warning  Failed     14s (x3 over 57s)  kubelet            Error: ErrImagePull
  Normal   BackOff    2s (x4 over 56s)   kubelet            Back-off pulling image "ghcr.io/prabalpatra/kairos-backend:v999.0.0-nonexistent"
  Warning  Failed     2s (x4 over 56s)   kubelet            Error: ImagePullBackOff
```

### 3. Root cause
The deployment manifest specifies an image tag that was never built or pushed to the registry. The container runtime returns a 404/NotFound error during pull negotiation.

### 4. Fix and remediation
Update the container image to a valid release tag:
```bash
kubectl set image deployment/kairos-broken-image backend=ghcr.io/prabalpatra/kairos-backend:latest -n kairos
```

Verify rollout status:
```bash
kubectl rollout status deployment/kairos-broken-image -n kairos
```

The pod reaches `Running` status with `1/1` containers ready. Clean up the test deployment:
```bash
kubectl delete -f troubleshooting/broken-image.yaml
```

---

## Scenario 2: Service with empty endpoints and connection timeout

### 1. Failure description and manifest
File: `troubleshooting/broken-service.yaml`

The service defines port 8000 and targets port 8000, but sets its label selector to `app: kairos-unmatched-pod-label`. Because no pods in the cluster carry that label, the Kubernetes endpoint controller finds no matching target IP addresses.

### 2. Diagnosis steps
Apply the service:
```bash
kubectl apply -f troubleshooting/broken-service.yaml
```

Check the service and its registered endpoints:
```bash
kubectl get svc kairos-broken-service -n kairos
kubectl get endpoints kairos-broken-service -n kairos
```

Output:
```text
NAME                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
kairos-broken-service   ClusterIP   10.100.45.120   <none>        8000/TCP   20s

NAME                    ENDPOINTS   AGE
kairos-broken-service   <none>      20s
```

Notice that the `ENDPOINTS` column displays `<none>`.

Testing connectivity from inside the cluster using curl returns connection refused or a 502 Bad Gateway:
```bash
kubectl run test-curl --rm -it --image=curlimages/curl --restart=Never -n kairos -- curl -v --connect-timeout 3 http://kairos-broken-service:8000/health
```

Output:
```text
* Connection timed out after 3001 milliseconds
curl: (28) Failed to connect to kairos-broken-service port 8000: Connection timed out
```

### 3. Root cause
Kubernetes services route traffic based on label selectors matching `.metadata.labels` on running pods. When the selector string does not match any existing pod, the endpoints list remains empty (`<none>`), causing traffic to drop at the kube-proxy layer.

### 4. Fix and remediation
Compare existing pod labels:
```bash
kubectl get pods -n kairos --show-labels
```

Update the service selector to match running backend pods:
```bash
kubectl patch service kairos-broken-service -n kairos -p '{"spec":{"selector":{"app":"kairos-backend"}}}'
```

Re-check endpoints:
```bash
kubectl get endpoints kairos-broken-service -n kairos
```

Output:
```text
NAME                    ENDPOINTS                         AGE
kairos-broken-service   10.0.10.15:8000,10.0.10.84:8000   3m
```

Repeat the curl probe:
```bash
kubectl run test-curl --rm -it --image=curlimages/curl --restart=Never -n kairos -- curl -s http://kairos-broken-service:8000/health
```

Output:
```json
{"status":"healthy","service":"kairos-backend"}
```

Clean up the test service:
```bash
kubectl delete -f troubleshooting/broken-service.yaml
```
