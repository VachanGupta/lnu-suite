"""
lnu-suite scan module
Usage:
  python lnu/scan.py --host 127.0.0.1 --start 1 --end 1024 --workers 100 --timeout 0.3 --output scan.json
"""
import argparse
import socket
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, Optional, List, Dict, Any

def check_port(host: str, port: int, timeout: float = 0.5) -> Tuple[int, bool, Optional[str]]:
    """
    Checks a single port on a given host.
    Returns a tuple: (port, is_open, banner_or_none).
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        # Connection successful, port is open. Now try to grab a banner.
        s.settimeout(0.2)  # Short timeout for receiving data
        banner = None
        try:
            raw_banner = s.recv(1024)
            if raw_banner:
                # Attempt to decode, fall back to a raw representation if it fails
                try:
                    banner = raw_banner.decode(errors="ignore").strip()
                except Exception:
                    banner = repr(raw_banner)
        except (socket.timeout, OSError):
            # No banner received within the short timeout
            pass
        finally:
            s.close()
        return port, True, banner
    except (socket.timeout, ConnectionRefusedError, OSError):
        # Port is closed or not reachable
        try:
            s.close()
        except OSError:
            pass
        return port, False, None

def scan_range(host: str, start: int, end: int, workers: int, timeout: float) -> List[Dict[str, Any]]:
    """
    Scans a range of ports on a host using a thread pool.
    """
    open_ports = []
    print(f"Scanning {host} from port {start} to {end} with {workers} workers...")
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Create a future for each port check
        future_to_port = {executor.submit(check_port, host, port, timeout): port for port in range(start, end + 1)}
        
        # Process results as they complete
        for future in as_completed(future_to_port):
            port, is_open, banner = future.result()
            if is_open:
                result = {"port": port, "banner": banner}
                open_ports.append(result)
                print(f"[+] OPEN: Port {port} on {host} {'- ' + banner if banner else ''}")
                
    # Sort results by port number for clean output
    open_ports.sort(key=lambda x: x['port'])
    return open_ports

def main():
    """Main function to parse arguments and run the scanner."""
    parser = argparse.ArgumentParser(description="lnu scan: concurrent TCP port scanner")
    parser.add_argument("--host", required=True, help="Hostname or IP to scan")
    parser.add_argument("--start", type=int, default=1, help="The starting port")
    parser.add_argument("--end", type=int, default=1024, help="The ending port")
    parser.add_argument("--workers", type=int, default=200, help="Number of concurrent threads")
    parser.add_argument("--timeout", type=float, default=0.4, help="Connection timeout in seconds")
    parser.add_argument("--output", type=str, help="Optional path to save JSON results")
    args = parser.parse_args()

    # Important legal and ethical note
    print("\n*** WARNING: Only scan hosts you own or have explicit permission to test. ***\n")

    results = scan_range(args.host, args.start, args.end, args.workers, args.timeout)
    
    if args.output:
        print(f"\nScan complete. Saving results to {args.output}")
        try:
            with open(args.output, "w") as f:
                json.dump({"host": args.host, "open_ports": results}, f, indent=2)
        except IOError as e:
            print(f"Error writing to output file: {e}")
    else:
        print("\nScan complete.")

if __name__ == "__main__":
    main()
