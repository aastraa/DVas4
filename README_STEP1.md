# Step 1 — Prometheus + Node Exporter

Goal: run Prometheus and Node Exporter, verify both targets are UP.

## Files
- `docker-compose.yml`
- `prometheus.yml`

## Run
1) Open terminal in this folder.
2) Run: `docker compose up -d`
3) Open Prometheus UI: http://localhost:9090
4) Check **Status → Targets**: both `prometheus` and `node` should be **UP**.

## Quick PromQL to test
- `up`
- `process_cpu_seconds_total`
- `node_exporter_build_info`

If both targets are UP, proceed to Step 2 (add Grafana).
