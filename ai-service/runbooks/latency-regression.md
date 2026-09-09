# Latency regression

## Symptoms
- `processing-service` p95 latency is increasing over time.
- Prometheus `histogram_quantile(0.95, ...)` trend is `up` with `delta_pct > 10`.
- No single trace is an outlier; the regression is gradual.

## Likely cause
A gradual degradation of the third-party enrichment API or increased load on `processing-service`. The WireMock `slow` scenario delay may have been enabled, or the upstream is genuinely degrading.

## Mitigation
1. Compare current p95 with the 1h window baseline.
2. Check if `X-Scenario: slow` is being sent unintentionally.
3. Scale `processing-service` horizontally if load increased.
4. Contact the third-party provider about their latency.

## Related signals
- Metric: `histogram_quantile(0.95, sum by (le) (rate(http_server_request_duration_seconds_bucket{service_name="processing-service"}[5m])))`
- Metric: `http_client_request_duration_seconds{service_name="processing-service"}`
- Trend: `delta_pct` and `trend` fields from the p95 tool
