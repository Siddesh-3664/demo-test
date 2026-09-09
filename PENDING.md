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
| S3.4 verify-s3.ps1 | yes | no (Docker Desktop down); PowerShell syntax check PASS | PENDING |

## Status of Sprint 4 tasks
| Task | Files written | Acceptance run | Acceptance result |
|---|---|---|---|
| S4.1 Ollama on host | n/a (host install) | no (Ollama not installed) | PENDING |
| S4.2 Python skeleton + /health | yes | no (Docker + Ollama needed) | PENDING |
| S4.3 schemas + budget | yes | yes (pytest 5/5 pass) | PASS |
| S4.4 Jaeger tool | yes | yes (pytest 13/13 pass); live test pending Docker | PASS (unit) |
| S4.5 intent router | yes | yes (pytest 11/11 pass) | PASS |
| S4.6 LLM client + prompt | yes | no (needs Ollama) | PENDING |
| S4.7 pipeline + /chat | yes | no (needs Docker + Ollama) | PENDING |
| S4.8 eval v0 | yes | no (needs Docker + Ollama) | PENDING |
| S4.9 verify-s4.ps1 | yes | no (needs Docker + Ollama) | PENDING |

## Status of Sprint 5 tasks
| Task | Files written | Acceptance run | Acceptance result |
|---|---|---|---|
| S5.1 Prometheus config | yes | no (needs Docker) | PENDING |
| S5.2 Grafana datasources | yes | no (needs Docker) | PENDING |
| S5.3 Services dashboard | yes | no (needs Docker) | PENDING |
| S5.4 Prometheus tool | yes | yes (pytest 5/5 pass) | PASS (unit) |
| S5.5 Wire TREND | yes | no (needs Docker + Ollama) | PENDING |
| S5.6 eval + verify | yes | no (needs Docker + Ollama) | PENDING |

## Status of Sprint 6 tasks
| Task | Files written | Acceptance run | Acceptance result |
|---|---|---|---|
| S6.1 Loki config | yes | no (needs Docker) | PENDING |
| S6.2 Grafana trace↔logs | n/a (manual) | no (needs Docker) | PENDING |
| S6.3 Loki tool | yes | yes (pytest 6/6 pass) | PASS (unit) |
| S6.4 Wire WHY_FAIL | yes | no (needs Docker + Ollama) | PENDING |
| S6.5 eval + verify | yes | no (needs Docker + Ollama) | PENDING |

## Status of Sprint 7 tasks
| Task | Files written | Acceptance run | Acceptance result |
|---|---|---|---|
| S7.1 Scaffold | yes | no (needs npm install) | PENDING |
| S7.2 TriggerPanel | yes | no (needs npm + Docker) | PENDING |
| S7.3 ChatPanel | yes | no (needs npm + Docker) | PENDING |
| S7.4 verify-s7.ps1 | yes | no (needs npm + Docker) | PENDING |

## Status of Sprint 8 tasks
| Task | Files written | Acceptance run | Acceptance result |
|---|---|---|---|
| S8.1 Runbooks + Chroma | yes | yes (pytest 4/4 pass); live needs Ollama | PASS (unit) |
| S8.2 Wire KNOWN + fallback | yes | no (needs Docker + Ollama) | PENDING |
| S8.3 Frontend update | yes | no (needs npm) | PENDING |
| S8.4 Full eval suite | yes | no (needs Docker + Ollama) | PENDING |
| S8.5 LangGraph (optional) | skipped | n/a | CLOSED |
| S8.6 verify + demo | yes | no (needs Docker + Ollama) | PENDING |

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
