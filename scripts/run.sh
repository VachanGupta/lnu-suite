
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VENVDIR="${ROOT}/venv"

echo "--- Setting up Python virtual environment ---"
if [ ! -d "$VENVDIR" ]; then
  echo "Virtual environment not found. Creating one..."
  python3 -m venv venv
fi

source venv/bin/activate
echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo -e "\n--- Building C++ process utility (lnu-proc) ---"
mkdir -p bin
if ! command -v g++ &> /dev/null
then
    echo "g++ compiler not found. Please install it (e.g., 'sudo apt install build-essential')."
    exit 1
fi
g++ -std=gnu++17 cpp/lnu_proc.cpp -o bin/lnu-proc || { echo "C++ build failed"; exit 1; }
echo "Build successful. Binary is at bin/lnu-proc"

echo -e "\n--- Starting lnu-suite Demo ---"

echo -e "\n[1] Starting monitor in the background (5s interval, 20s duration)..."
python3 lnu/monitor.py --interval 5 --duration 20 --out logs/monitor.log &
MON_PID=$!
echo "Monitor started with PID=$MON_PID"

sleep 1

echo -e "\n[2] Running a quick scan on localhost ports 20-1024..."
python3 lnu/scan.py --host 127.0.0.1 --start 20 --end 1024 --workers 200 --timeout 0.2 --output logs/scan.json

if [[ "$(uname)" == "Linux" ]]; then
    echo -e "\n[3] Listing current processes with lnu-proc (top 20):"
    ./bin/lnu-proc list | head -n 20
else
    echo -e "\n[3] Skipping process list: lnu-proc requires a Linux /proc filesystem."
fi


echo -e "\n--- Waiting for monitor process ($MON_PID) to finish ---"

wait $MON_PID || true 
echo "Monitor has finished."

echo -e "\n--- Demo Complete ---"
echo "Check logs/monitor.log and logs/scan.json for output."
