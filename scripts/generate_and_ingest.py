import argparse
import json
import random
import time
from pathlib import Path
import httpx

EVENT_TYPES = ["route_start", "route_update", "reroute", "route_complete"]

def make_event(i: int, malformed_rate: float) -> dict:
    malformed = random.random() < malformed_rate
    event_type = random.choice(EVENT_TYPES)
    predicted = random.uniform(300, 3600)
    actual = max(1, predicted + random.gauss(0, 120))
    latency = random.uniform(5, 150)

    if malformed:
        choice = random.choice(["type", "eta", "latency"])
        if choice == "type":
            event_type = "unknown_event"
        elif choice == "eta":
            predicted = -1
        else:
            latency = -5

    return {
        "vehicle_id": f"vehicle-{i % 2000}",
        "route_id": f"route-{i // 4}",
        "event_type": event_type,
        "predicted_eta_sec": round(predicted, 2),
        "actual_eta_sec": round(actual, 2),
        "latency_ms": round(latency, 2),
        "rerouted": event_type == "reroute",
        "completed": event_type == "route_complete" or random.random() > 0.08,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10000)
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--malformed-rate", type=float, default=0.02)
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()

    started = time.perf_counter()
    accepted = rejected = 0

    with httpx.Client(timeout=120.0) as client:
        for start in range(0, args.count, args.batch_size):
            batch = [
                make_event(i, args.malformed_rate)
                for i in range(start, min(start + args.batch_size, args.count))
            ]
            response = client.post(f"{args.base_url}/events/batch", json=batch)
            response.raise_for_status()
            body = response.json()
            accepted += body["accepted"]
            rejected += body["rejected"]

    elapsed = time.perf_counter() - started
    result = {
        "events_sent": args.count,
        "accepted": accepted,
        "rejected": rejected,
        "elapsed_seconds": round(elapsed, 3),
        "events_per_second": round(args.count / elapsed, 2) if elapsed else 0,
        "batch_size": args.batch_size,
        "malformed_rate": args.malformed_rate,
    }

    print(json.dumps(result, indent=2))
    Path("benchmark_results.json").write_text(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
