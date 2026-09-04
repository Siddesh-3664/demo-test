# Pending items

## Resolved: Docker Desktop
- Docker Desktop is now running. CLI at `C:\Users\siddesh.chavadi\AppData\Local\Programs\DockerDesktop\resources\bin`.
- Add to PATH for new shells: `$env:Path = "C:\Users\siddesh.chavadi\AppData\Local\Programs\DockerDesktop\resources\bin;$env:Path"`

## Sprint gates run
- `.\scripts\verify-s0.ps1` → `SPRINT 0 GREEN` (compose config valid, postgres healthy, otel jar present)
- `.\scripts\verify-s1.ps1` → `SPRINT 1 GREEN` (3 orders → 201, 3 rows written, validation → 400)
- `.\scripts\verify-s2.ps1` → `SPRINT 2 GREEN` (fast/slow/fail scenarios, ERROR log present)

## Status of Sprint 3 tasks
| Task | Files written | Acceptance run | Acceptance result |
|---|---|---|---|
| S3.1 collector config + Jaeger | yes | yes (collector ready, jaeger 200) | PASS |
| S3.2 attach agent to 3 services | yes | no (Docker Desktop down) | PENDING |
| S3.3 return real traceId | yes | no (Docker Desktop down) | PENDING |

## Status of Sprint 0 tasks
| Task | Files written | Acceptance run | Acceptance result |
|---|---|---|---|
| S0.1 folder layout + .env | yes | yes (Get-ChildItem) | PASS |
| S0.2 OTEL java agent jar | yes | yes (`-gt 15MB` = True) | PASS |
| S0.3 docker-compose.yml | yes | yes (verify-s0.ps1) | PASS |
| S0.4 lib.ps1 + verify-s0.ps1 | yes | yes (verify-s0.ps1) | PASS |

## Status of Sprint 1 tasks
| Task | Files written | Acceptance run | Acceptance result |
|---|---|---|---|
| S1.1 persistence-service | yes | yes (verify-s1.ps1) | PASS |
| S1.2 processing-service | yes | yes (verify-s1.ps1) | PASS |
| S1.3 order-service | yes | yes (verify-s1.ps1) | PASS |
| S1.4 verify-s1.ps1 | yes | yes (verify-s1.ps1) | PASS |
