"""
lnu-suite monitor module
Usage:
  python lnu/monitor.py --interval 2 --duration 60 --out logs/monitor.log
Outputs newline-delimited JSON, one snapshot per sample.
"""
import argparse
import json
import time
import os
import signal
from typing import Dict
import psutil

STOP = False

def signal_handler(signum, frame):
    global STOP
    print("\nSignal received, preparing to exit...")
    STOP = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_snapshot() -> Dict:
    now = time.time()
    cpu = psutil.cpu_percent(interval=None)
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters(pernic=True)
    net_out = {}
    for nic, stats in net.items():
        net_out[nic] = {
            "bytes_sent": stats.bytes_sent,
            "bytes_recv": stats.bytes_recv,
            "packets_sent": stats.packets_sent,
            "packets_recv": stats.packets_recv
        }
    return {
        "ts": now,
        "cpu_percent": cpu,
        "virtual_memory": {"total": vm.total, "used": vm.used, "percent": vm.percent},
        "disk": {"total": disk.total, "used": disk.used, "percent": disk.percent},
        "net": net_out
    }

def rotate_if_needed(path: str, max_bytes: int = 2_000_000):
    """Rotate log file if it exceeds max_bytes."""
    if not os.path.exists(path):
        return
    if os.path.getsize(path) > max_bytes:
        i = 1
        while True:
            new_path = f"{path}.{i}"
            if not os.path.exists(new_path):
                print(f"Rotating log file {path} to {new_path}")
                os.rename(path, new_path)
                break
            i += 1

def main():
    """Main function to run the monitor loop."""
    parser = argparse.ArgumentParser(description="lnu monitor: sample system stats")
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds between samples")
    parser.add_argument("--duration", type=float, default=60.0, help="How long to run in seconds")
    parser.add_argument("--out", type=str, default="logs/monitor.log", help="JSONL output path")
    args = parser.parse_args()

    end_time = time.time() + args.duration
    # Ensure the directory for the output file exists
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    print(f"Starting monitor. Logging to {args.out} for {args.duration} seconds.")
    print("Press Ctrl+C to exit early.")

    while not STOP and time.time() < end_time:
        rotate_if_needed(args.out)
        snap = get_snapshot()
        try:
            with open(args.out, "a") as f:
                f.write(json.dumps(snap) + "\n")
        except IOError as e:
            print(f"Error writing to log file: {e}")
            break
            
        slept = 0.0
        while slept < args.interval and not STOP and time.time() < end_time:
            time.sleep(0.2)
            slept += 0.2

    print("Monitor: exiting cleanly.")

if __name__ == "__main__":
    main()
