# Navigation Telemetry Validator

A Tesla-shaped validation project for practicing Linux, telemetry pipelines, testing,
observability, CI/CD, and data-based quality assessment.

## What it does

- Generates synthetic navigation telemetry
- Ingests batches through a FastAPI service
- Validates malformed/suspicious events
- Stores events in PostgreSQL
- Computes route-quality metrics
- Exposes `/health` and `/metrics/summary`
- Produces structured logs for debugging
- Includes pytest tests and GitHub Actions CI
- Includes Docker Compose
- Includes a Linux `systemd` service example
- Includes a benchmark script so resume metrics come from real runs

## Tech

Python, FastAPI, PostgreSQL, SQLAlchemy, Docker, Docker Compose, pytest,
GitHub Actions, Linux/systemd

## Metrics

The API computes:

- route completion rate
- reroute rate
- malformed event rate
- average ETA error
- p95 ingestion latency
- total events

## Quick start

Install Docker Desktop, open a terminal in this folder, then run:

```bash
docker compose up --build
```

In a second terminal:

```bash
docker compose exec api python scripts/generate_and_ingest.py --count 10000
```

Open:

```text
http://localhost:8000/health
http://localhost:8000/metrics/summary
http://localhost:8000/docs
```

## Run 100,000 events

```bash
docker compose exec api python scripts/generate_and_ingest.py --count 100000
```

The script prints real measured throughput and writes `benchmark_results.json`.

## Run tests

```bash
docker compose exec api pytest -q
```

## Failure / bad-data test

```bash
docker compose exec api python scripts/generate_and_ingest.py --count 5000 --malformed-rate 0.08
```

Then inspect:

```text
http://localhost:8000/metrics/summary
```

## Linux practice

While the app is running, practice:

```bash
docker ps
docker logs -f navigation-api
ps aux | grep python
curl http://localhost:8000/health
curl http://localhost:8000/metrics/summary
ss -ltnp
```

On Ubuntu, adapt and install `deploy/navigation-validator.service`:

```bash
sudo cp deploy/navigation-validator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable navigation-validator
sudo systemctl start navigation-validator
sudo systemctl status navigation-validator
journalctl -u navigation-validator -f
```

## Resume rule

Only claim numbers after you personally run the benchmark.

Safe qualitative bullet after completing the project:

> Built a Python/Linux navigation telemetry validation platform that ingests synthetic route events, computes route-quality metrics, flags malformed telemetry, persists data in PostgreSQL, and exposes health/metrics APIs.
