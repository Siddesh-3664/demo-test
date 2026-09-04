# Pending items

## Docker Desktop (blocks Sprint 0 acceptance)
- Docker is not installed / not on PATH in this environment.
- `Get-Command docker` / `docker.exe` / `docker-compose` all return nothing; no `com.docker.*` service registered.
- Acceptance commands that require Docker and have NOT been run yet:
  - S0.3: `docker compose -f demo\docker-compose.yml config --quiet; $LASTEXITCODE` then `docker compose -f demo\docker-compose.yml up -d postgres` → expect `0` then `demo-postgres-1 healthy`
  - S0.4: `.\demo\scripts\verify-s0.ps1` → expect three `ok:` lines and `SPRINT 0 GREEN`
- Once Docker Desktop is installed and running, run `.\demo\scripts\verify-s0.ps1` to gate Sprint 0.
- Sprint 1 (services) cannot start until `verify-s0.ps1` exits 0 (Brief: "Prerequisite: Sprint 0 green").

## Status of Sprint 0 tasks
| Task | Files written | Acceptance run | Acceptance result |
|---|---|---|---|
| S0.1 folder layout + .env | yes | yes (Get-ChildItem) | PASS |
| S0.2 OTEL java agent jar | yes | yes (`-gt 15MB` = True) | PASS |
| S0.3 docker-compose.yml | yes | no (Docker missing) | PENDING |
| S0.4 lib.ps1 + verify-s0.ps1 | yes | no (Docker missing); PowerShell syntax check PASS | PENDING |

## Status of Sprint 1 tasks
| Task | Files written | Acceptance run | Acceptance result |
|---|---|---|---|
| S1.1 persistence-service | yes | no (Docker missing) | PENDING |
| S1.2 processing-service | yes | no (Docker missing) | PENDING |
| S1.3 order-service | yes | no (Docker missing) | PENDING |
| S1.4 verify-s1.ps1 | yes | no (Docker missing); PowerShell syntax check PASS | PENDING |
