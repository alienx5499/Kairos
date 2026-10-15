# Kairos: Incident Response and Outage Management

Kairos is an incident tracking web application built for the SST DevOps Capstone Project. It lets teams log outages, set severity levels (P1–P4), update statuses, view real-time metrics, and document root causes.

## Architecture overview

The application is built with a React frontend, a FastAPI backend, and a PostgreSQL database:

<img width="8192" height="2164" alt="Architecture Overview" src="https://github.com/user-attachments/assets/9c2a67f6-3dca-4ec7-9e64-df60396f8315" />

## Repository structure

```text
kairos/
├── .github/
│   └── workflows/
│       └── ci-cd.yml                   # CI/CD and Trivy security scanning
├── backend/
│   ├── alembic/                        # Database migrations
│   ├── app/
│   │   ├── domain/                     # Incident models and enums
│   │   ├── application/                # Business logic and repository interfaces
│   │   ├── infrastructure/             # Database models, connection pool, and metrics
│   │   ├── interfaces/                 # API routes, schemas, and health endpoints
│   │   └── main.py                     # FastAPI application entrypoint
│   ├── tests/
│   │   └── test_incidents.py           # Backend pytest suite
│   ├── Dockerfile                      # Multi-stage Python build
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/                 # React UI components
│   │   ├── App.jsx                     # Dashboard view
│   │   └── index.css                   # Styles
│   ├── nginx.conf                      # Nginx reverse proxy configuration
│   └── Dockerfile                      # Multi-stage Node and Nginx build
├── helm/
│   └── kairos/                         # Helm chart templates and values
├── k8s/
│   └── namespace.yaml                  # Kubernetes namespace manifest
├── monitoring/
│   ├── grafana-dashboard.json          # Grafana dashboard definition
│   ├── grafana-values.yaml             # Grafana Helm values
│   └── prometheus-values.yaml          # Prometheus scraping configuration
├── terraform/
│   ├── vpc.tf                          # AWS VPC and networking resources
│   ├── eks.tf                          # AWS EKS cluster and node group
│   ├── main.tf                         # Terraform AWS provider configuration
│   ├── variables.tf                    # Terraform variables
│   └── outputs.tf                      # Terraform outputs
├── troubleshooting/
│   ├── RCA.md                          # Root cause analysis guide
│   ├── broken-image.yaml               # ImagePullBackOff test manifest
│   └── broken-service.yaml             # Service selector mismatch test manifest
└── docker-compose.yml                  # Local Docker Compose setup
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

<img width="3024" height="676" alt="image" src="https://github.com/user-attachments/assets/080fe117-3a0f-475b-960a-69f77d9aa81a" />

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

<img width="1512" height="827" alt="Frontend UI" src="https://github.com/user-attachments/assets/c9c82610-ba9a-4b84-9a33-86b9198258ef" />

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

## Security and vulnerability scanning (DevSecOps)

The pipeline uses Trivy to scan backend and frontend container images for known vulnerabilities (CVEs). Unfixed upstream vulnerabilities are ignored (`--ignore-unfixed`), and the build fails if actionable HIGH or CRITICAL CVEs are detected.

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

5. Apply:
```bash
terraform apply
```

The configuration defines an AWS VPC across two Availability Zones (public and private subnets, Internet Gateway, NAT Gateway) and an EKS cluster with managed node groups.

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

Helm configuration values for Prometheus and Grafana are in `monitoring/prometheus-values.yaml` and `monitoring/grafana-values.yaml`. The Grafana dashboard in `monitoring/grafana-dashboard.json` displays request throughput, latencies, and active incidents.

## Troubleshooting scenarios

The `troubleshooting/` directory contains two Kubernetes failure scenarios and a post-mortem guide:
- `broken-image.yaml`: reproduces an `ImagePullBackOff` error from an invalid image tag
- `broken-service.yaml`: reproduces a service with empty endpoints caused by a selector mismatch
- `RCA.md`: diagnosis steps, log outputs, root cause analysis, and fixes
