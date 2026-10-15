from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

HTTP_REQUESTS_TOTAL = Counter(
    "kairos_http_requests_total",
    "Total HTTP requests handled by Kairos",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "kairos_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

# incident gauges mirror the database, set on every scrape
INCIDENTS_TOTAL = Gauge(
    "kairos_incidents_total",
    "Total incidents on record in Kairos"
)

ACTIVE_INCIDENTS_GAUGE = Gauge(
    "kairos_active_incidents",
    "Current active (unresolved) incidents",
    ["severity"]
)


def record_incident_state(total: int, active_by_severity: dict[str, int]) -> None:
    INCIDENTS_TOTAL.set(total)
    for severity, count in active_by_severity.items():
        ACTIVE_INCIDENTS_GAUGE.labels(severity=severity).set(count)


def get_metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
