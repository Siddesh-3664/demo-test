# Database write failures

## Symptoms
- `persistence-service` returns 500.
- Jaeger span `INSERT orders` has `error=true`.
- Loki ERROR log in `persistence-service`.
- Postgres connection errors or constraint violations.

## Likely cause
The `orders` table insert failed. Possible causes: Postgres is down, connection pool exhausted, or a constraint violation on the `orders` table.

## Mitigation
1. Check Postgres health: `docker compose ps postgres`.
2. Verify the `orders` table exists: `docker compose exec postgres psql -U demo -d demo -c '\dt'`.
3. If the connection pool is exhausted, increase `spring.datasource.hikari.maximum-pool-size`.
4. For constraint violations, check the data being inserted.

## Related signals
- Span: `INSERT orders` in `persistence-service`
- Metric: `http_server_request_duration_seconds_count{service_name="persistence-service",http_response_status_code=~"5.."}`
- Log: `persistence-service` ERROR
