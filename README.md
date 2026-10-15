# Kairos: Incident Response and Outage Management

Kairos is an incident tracking web application built for the SST DevOps Capstone Project. It lets teams log outages, set severity levels (P1 to P4), update statuses, view real-time metrics, and document root causes.

## Architecture overview

The application is built with a React frontend, a FastAPI backend, and a PostgreSQL database:

<img width="8192" height="2164" alt="Architecture Overview" src="https://github.com/user-attachments/assets/9c2a67f6-3dca-4ec7-9e64-df60396f8315" />

## Repository structure

```text
kairos/
├── .github/
│   └── workflows/
│       └── ci-cd.yml                   # Test, build, Trivy scan, GHCR push, Helm deploy
├── backend/
│   ├── alembic/
│   │   └── versions/
│   │       └── 0001_initial_incidents.py  # Initial incidents table migration
│   ├── app/
│   │   ├── domain/                     # Incident entity, severity and status enums
│   │   ├── application/                # Use cases and repository interface
│   │   ├── infrastructure/             # SQLAlchemy models, repository, metrics
│   │   ├── interfaces/                 # API routes, schemas, health and /metrics
│   │   ├── config.py                   # Settings from environment variables
│   │   └── main.py                     # FastAPI entrypoint and metrics middleware
│   ├── tests/
│   │   └── test_incidents.py           # Pytest suite on in-memory SQLite
│   ├── alembic.ini
│   ├── pytest.ini
│   ├── requirements.txt
│   └── Dockerfile                      # Multi-stage Python build, non-root user
├── frontend/
│   ├── src/
│   │   ├── components/                 # IncidentList, IncidentModal, Desk
│   │   ├── App.jsx                     # Dashboard layout and polling
│   │   ├── api.js                      # Backend API client
│   │   ├── incident.js                 # Severity, status and time helpers
│   │   └── index.css                   # Styles
│   ├── nginx.conf                      # Serves the build and proxies /api
│   └── Dockerfile                      # Multi-stage Node build and Nginx runtime
├── helm/
│   └── kairos/
│       ├── templates/                  # Deployments, services, ingress, HPA, postgres
│       ├── values.yaml                 # Default values
│       ├── values-dev.yaml             # Development overrides
│       └── values-prod.yaml            # Production overrides
├── k8s/
│   ├── namespace.yaml                  # Kubernetes namespace
│   ├── deployment.yaml                 # Standalone deployment manifest
│   └── service.yaml                    # Standalone service manifest
├── monitoring/
│   ├── prometheus-values.yaml          # Prometheus Helm values and scrape job
│   ├── grafana-values.yaml             # Grafana Helm values with datasource and dashboard
│   ├── grafana-dashboard.json          # Grafana dashboard definition
│   └── prometheus.yml                  # Prometheus config for Docker Compose
├── terraform/
│   ├── main.tf                         # AWS provider configuration
│   ├── vpc.tf                          # VPC, subnets, gateways and routes
│   ├── eks.tf                          # EKS cluster and node group
│   ├── variables.tf                    # Input variables
│   ├── outputs.tf                      # Cluster and network outputs
│   └── terraform.tfvars.example        # Example variables, no credentials
├── troubleshooting/
│   ├── RCA.md                          # Root cause analysis guide
│   ├── broken-image.yaml               # ImagePullBackOff test manifest
│   └── broken-service.yaml             # Service selector mismatch test manifest
├── docker-compose.yml                  # Local stack: frontend, backend, postgres, prometheus
├── Kairos_Demo.mp4                     # Narrated project walkthrough
├── Kairos_Presentation.pptx            # Final presentation slides
└── README.md
```

## Running backend tests

The tests run with pytest against an in-memory SQLite database:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

<img width="1512" height="297" alt="Pytest passing test suite" src="https://github.com/user-attachments/assets/0479799e-0dda-4acc-9837-3578b0061cbe" />

The suite checks incident creation, status transitions, schema validation, health checks, and metrics endpoints.

## Git version control and commit history

Commit history for the repository:

```bash
git log --format='%h | %ad | %s' --date=short
```

<img width="3024" height="676" alt="Git log" src="https://github.com/user-attachments/assets/080fe117-3a0f-475b-960a-69f77d9aa81a" />

Repository and commit history on GitHub:

<img width="1512" height="792" alt="GitHub repository" src="https://github.com/user-attachments/assets/c3b2c986-ec22-428a-80ef-63c4dbd26d52" />

<img width="1512" height="827" alt="GitHub commit history" src="https://github.com/user-attachments/assets/d4e6384c-89f3-4ce7-b8bd-2d727ab1bead" />

## Running locally with Docker Compose

1. Copy the environment file:
```bash
cp .env.example .env
```

2. Build the images:
```bash
docker compose build
```

<img width="1512" height="810" alt="Docker Compose build" src="https://github.com/user-attachments/assets/cbe76bfe-5d46-4a1e-96c6-6460e66fdfd5" />

3. Start the containers:
```bash
docker compose up -d
```

<img width="1511" height="90" alt="Docker Compose up" src="https://github.com/user-attachments/assets/54f1b50e-0cc4-46c9-b31e-e8ccc5fb4d27" />

4. Check running containers:
```bash
docker compose ps
```

<img width="1512" height="92" alt="Docker Compose ps" src="https://github.com/user-attachments/assets/f90f8f2f-a553-468b-be2c-a2b11e67bb2d" />

5. Check backend logs:
```bash
docker compose logs backend
```

<img width="1512" height="272" alt="Backend logs" src="https://github.com/user-attachments/assets/faaa65bd-35f7-44c0-9744-eb1627e5bdd9" />

6. Open the application:
- Frontend: http://localhost:3000

<img width="1512" height="950" alt="Frontend UI" src="https://github.com/user-attachments/assets/4ad02a32-42d0-420b-a18e-fea006ea6bc0" />

- Swagger API docs: http://localhost:8000/docs

<img width="1512" height="828" alt="Swagger API docs" src="https://github.com/user-attachments/assets/6bc499a3-e516-4253-afc0-5fcafb763a5e" />

- Health check: http://localhost:8000/health

<img width="1512" height="127" alt="Health check response" src="https://github.com/user-attachments/assets/85e93355-fc27-456c-a198-93d8f2317650" />

7. Tear down the containers:
```bash
docker compose down -v
```

## CI/CD pipeline (GitHub Actions)

The workflow file in `.github/workflows/ci-cd.yml` runs on pushes to `main` and on pull requests:
1. Runs tests with `pytest`.
2. Builds Docker images for the frontend and backend.
3. Scans images for vulnerabilities using Trivy.
4. Pushes images to GitHub Container Registry (GHCR) tagged with the commit SHA (`ghcr.io/<owner>/kairos-backend:<sha>`).
5. Deploys the new images to EKS with `helm upgrade --install`.

A successful pipeline run:

<img width="1512" height="462" alt="Successful GitHub Actions pipeline run" src="https://github.com/user-attachments/assets/1734701f-153d-4c14-b678-d1c53cfb461c" />

Images published to GHCR, tagged with the commit SHA:

<img width="946" height="316" alt="GHCR packages" src="https://github.com/user-attachments/assets/522d35ce-5a02-474d-a3f3-15a8f3762de5" />

<img width="1511" height="789" alt="GHCR image versions tagged with commit SHA" src="https://github.com/user-attachments/assets/e8279ca6-9e3d-4a91-8d60-aee2c4cf6f96" />

## Security and vulnerability scanning (DevSecOps)

The pipeline uses Trivy to scan backend and frontend container images for known vulnerabilities (CVEs). Unfixed upstream vulnerabilities are ignored (`--ignore-unfixed`), and the build fails if actionable HIGH or CRITICAL CVEs are detected.

<img width="1512" height="826" alt="Trivy scan report for the backend image" src="https://github.com/user-attachments/assets/f208abad-2021-49e1-b74d-dd178dc40547" />

## Provisioning AWS infrastructure with Terraform

1. Change to the terraform directory:
```bash
cd terraform
```

2. Copy the example variables file:
```bash
cp terraform.tfvars.example terraform.tfvars
```

3. Validate configuration:
```bash
terraform validate
```

<img width="1512" height="49" alt="Terraform Validate" src="https://github.com/user-attachments/assets/c3f3f750-74ff-49ae-9140-8fcda92c7933" />

4. Initialize and plan:
```bash
terraform init
terraform plan
```

<img width="3024" height="502" alt="Terraform Plan Output" src="https://github.com/user-attachments/assets/5b6db54a-a951-4cf3-964e-5f61c43391b9" />

5. Apply:
```bash
terraform apply
```

<img width="3024" height="1508" alt="Terraform Apply Output" src="https://github.com/user-attachments/assets/c37efe9a-5935-4b52-a7dd-c67dbff722f8" />

6. Clean up resources:
```bash
terraform destroy
```

<img width="3024" height="398" alt="Terraform Destroy Output" src="https://github.com/user-attachments/assets/7d9077c3-aa8c-49f2-abb2-57d747a5d62f" />

The configuration defines an AWS VPC across two Availability Zones (public and private subnets, Internet Gateway, NAT Gateway) and an EKS cluster with managed node groups.

Provisioned resources in the AWS Console (ap-southeast-2):

<img width="1512" height="801" alt="AWS VPC resource map" src="https://github.com/user-attachments/assets/f0d85718-1641-47ef-91f3-0b654b2ee7ee" />

<img width="1512" height="731" alt="AWS VPC subnets" src="https://github.com/user-attachments/assets/69f3a3f0-edfb-4a7d-947f-44b3b72bbf35" />

<img width="1512" height="681" alt="AWS EKS cluster" src="https://github.com/user-attachments/assets/7bf888e4-91a6-4d34-8b26-b2ea1d49fbde" />

<img width="1512" height="782" alt="AWS EKS node group" src="https://github.com/user-attachments/assets/3c96593a-a84d-46eb-bee0-9bf77d7ea99f" />

## Kubernetes deployment with Helm

1. Create the namespace:
```bash
kubectl apply -f k8s/namespace.yaml
```

2. Lint the chart:
```bash
helm lint helm/kairos
```

<img width="1512" height="79" alt="Helm lint" src="https://github.com/user-attachments/assets/4dc31978-4ac5-4667-9e7e-29629212df81" />

3. Render manifests:
```bash
helm template kairos ./helm/kairos
```

<img width="1512" height="569" alt="Helm template output" src="https://github.com/user-attachments/assets/a3ab1098-da31-4526-a55f-327bdc659f71" />

4. Deploy with development values:
```bash
helm upgrade --install kairos helm/kairos -f helm/kairos/values-dev.yaml -n kairos
```

5. Deploy with production values:
```bash
helm upgrade --install kairos helm/kairos -f helm/kairos/values-prod.yaml -n kairos
```

6. Install the ingress-nginx controller (provisions an AWS load balancer for the Ingress):
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx --version 4.15.1 \
  -n ingress-nginx --create-namespace --set controller.service.type=LoadBalancer
```

7. Check the nodes and pods on EKS:
```bash
kubectl get nodes
kubectl get pods -n kairos -o wide
```

<img width="1512" height="269" alt="kubectl get nodes and pods on EKS" src="https://github.com/user-attachments/assets/f1e7a045-f2a6-4d9c-975d-91ebc8f32a1b" />

8. Check the services and the Ingress address:
```bash
kubectl get svc,ingress -n kairos
```

<img width="1512" height="177" alt="kubectl get svc and ingress" src="https://github.com/user-attachments/assets/fd924142-cccd-4b39-bdb5-bd1514616317" />

9. List the Helm releases:
```bash
helm list -A
```

<img width="1512" height="141" alt="Helm releases" src="https://github.com/user-attachments/assets/34e59c32-13c1-4a55-b603-2829dd4ebe9c" />

Each push to `main` deploys a new revision through the pipeline and rolls the pods:
```bash
helm history kairos -n kairos
kubectl get pods -n kairos
```

<img width="1512" height="313" alt="Helm revision rolled out by the pipeline" src="https://github.com/user-attachments/assets/8c5d04ef-2076-45d2-a0f1-68bb3263f6e0" />

10. Open the application through the Ingress. The Ingress routes `/` to the frontend and `/api`, `/health`, `/metrics` to the backend for host `kairos.internal`, so map that host to the load balancer IP first:
```bash
dig +short $(kubectl get ingress kairos-ingress -n kairos -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "<load-balancer-ip> kairos.internal" | sudo tee -a /etc/hosts
```

- Application: http://kairos.internal

<img width="1512" height="952" alt="Application through the Ingress" src="https://github.com/user-attachments/assets/b1cbe241-2a9e-4874-a251-bbbf958ffd4a" />

## Observability and monitoring

The backend exposes Prometheus metrics on `/metrics`:
- `kairos_http_requests_total`: request count by method, path, and status code
- `kairos_http_request_duration_seconds`: request latency histogram
- `kairos_incidents_total`: total declared incidents
- `kairos_active_incidents`: active incident count

```bash
curl -s http://localhost:8000/metrics | grep -E '^# HELP (kairos_|http_requests)' -A 1
```

<img width="1512" height="221" alt="Prometheus metrics output" src="https://github.com/user-attachments/assets/76c8fdb5-4ae1-465a-88a4-98a5b01b07bf" />

The same endpoint on EKS, through the Ingress:

```bash
curl -s http://kairos.internal/metrics | grep -E '^kairos_' | head -20
```

<img width="1512" height="419" alt="Prometheus metrics on EKS through the Ingress" src="https://github.com/user-attachments/assets/0b5cd806-059c-4fdc-9587-cd45550d199a" />

The incident gauges are read from Postgres on every scrape, so they always match the database:
```bash
curl -s http://kairos.internal/metrics | grep -E '^kairos_(incidents_total|active_incidents)'
```

<img width="1512" height="138" alt="Incident gauges from the database" src="https://github.com/user-attachments/assets/3e0e6064-e634-42dd-ac5e-b14cee334b1a" />

Helm configuration values for Prometheus and Grafana are in `monitoring/prometheus-values.yaml` and `monitoring/grafana-values.yaml`. The Grafana dashboard in `monitoring/grafana-dashboard.json` displays request throughput, latencies, and active incidents.

1. Install Prometheus and Grafana in the cluster:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm upgrade --install prometheus prometheus-community/prometheus --version 29.37.0 \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml
helm upgrade --install grafana grafana/grafana --version 10.5.15 \
  -n monitoring -f monitoring/grafana-values.yaml
```

2. Open the Prometheus targets page:
```bash
kubectl port-forward -n monitoring svc/prometheus-server 9091:80
```

- Targets: http://localhost:9091/targets

<img width="1510" height="487" alt="Prometheus targets with kairos-backend up" src="https://github.com/user-attachments/assets/ea11eac6-430e-4d15-8435-8fd967ab4286" />

3. Open the Grafana dashboard (login `admin` with the `adminPassword` from `monitoring/grafana-values.yaml`):
```bash
kubectl port-forward -n monitoring svc/grafana 3001:80
```

- Dashboard: http://localhost:3001/d/kairos-sre-dashboard

<img width="1512" height="828" alt="Grafana dashboard with live incident, throughput and latency panels" src="https://github.com/user-attachments/assets/c9cc4cdb-cb2b-4ae2-bbe9-c103276e840e" />


## Troubleshooting scenarios

The `troubleshooting/` directory contains two Kubernetes failure scenarios and a post-mortem guide:
- `broken-image.yaml`: reproduces an `ImagePullBackOff` error from an invalid image tag
- `broken-service.yaml`: reproduces a service with empty endpoints caused by a selector mismatch
- `RCA.md`: diagnosis steps, log outputs, root cause analysis, and fixes

## Final presentation

The slide deck covers what Kairos is, why it was built, the tech stack, the pipeline, and the alternatives considered, with proof screenshots of the CI/CD run, the repository, Docker Compose, and the EKS deployment.

- Slides: [Kairos_Presentation.pptx](https://github.com/alienx5499/Kairos/blob/main/Kairos_Presentation.pptx)
- Demo video: [Kairos_Demo.mp4](https://github.com/alienx5499/Kairos/blob/main/Kairos_Demo.mp4)
