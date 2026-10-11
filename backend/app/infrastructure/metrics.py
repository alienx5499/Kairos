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

INCIDENTS_TOTAL = Counter(
    "kairos_incidents_total",
    "Total incidents reported in Kairos",
    ["severity", "service_name"]
)

ACTIVE_INCIDENTS_GAUGE = Gauge(
    "kairos_active_incidents",
    "Current active (unresolved) incidents",
    ["severity"]
)


def get_metrics_payload() -> tuple[bytes, str]:
    return generate_latest(), CONTENT_TYPE_LATEST
