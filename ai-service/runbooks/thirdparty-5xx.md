# Third-party 5xx errors

## Symptoms
- `processing-service` returns 502 to `order-service`.
- Jaeger span `POST wiremock:8080/thirdparty/enrich` has `error=true` and `http.response.status_code=500`.
- Loki ERROR log: `Third-party enrich failed: upstream unavailable`.
- Exception: `HttpServerErrorException` with 500 status.

## Likely cause
The third-party enrichment API returned HTTP 500 with body `{"error":"upstream unavailable"}`. The `X-Scenario: fail` WireMock mapping returns 500 after 300 ms.

## Mitigation
1. Check WireMock mappings for the `fail` scenario.
2. Retry with exponential backoff (max 3 attempts).
3. If persistent, fall back to a cached enrichment or return a degraded response.
4. Alert the third-party provider.

## Related signals
- Span: `POST wiremock:8080/thirdparty/enrich` (error=true)
- Metric: `http_server_request_duration_seconds_count{service_name="processing-service",http_response_status_code=~"5.."}`
- Log: `upstream unavailable`
