# Third-party timeouts

## Symptoms
- `processing-service` requests take > 2000 ms.
- Jaeger span `POST wiremock:8080/thirdparty/enrich` dominates the trace (pct >= 60).
- Prometheus `http_client_request_duration_seconds` p95 rising for `processing-service`.

## Likely cause
The third-party enrichment API at `POST wiremock:8080/thirdparty/enrich` is slow or unreachable. The `X-Scenario: slow` mapping adds a 2000-5000 ms delay. If the upstream is truly down, `SocketTimeoutException` is thrown.

## Mitigation
1. Check WireMock health: `curl http://localhost:8080/__admin/health`.
2. If the upstream is genuinely slow, increase the RestClient timeout or circuit-break.
3. Verify the `X-Scenario` header is not accidentally set to `slow` in production.

## Related signals
- Span: `POST wiremock:8080/thirdparty/enrich`
- Metric: `http_client_request_duration_seconds{service_name="processing-service"}`
- Log: `Third-party enrich failed`
