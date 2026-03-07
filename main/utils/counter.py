import json
from pathlib import Path
from main.utils.errors import CounterError

_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "invoice_counter.json"

def _read():
    if _FILE.exists():
        try:
            with open(_FILE) as f: return int(json.load(f).get("last",0))
        except: pass
    return 0

def _write(n):
    _FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_FILE,"w") as f: json.dump({"last":n},f)

def get_next_invoice_number():
    try:
        n = _read() + 1; _write(n); return n
    except OSError as e: raise CounterError(str(e))

def peek_current_number():
    try: return _read()
    except: return 0

def reset_counter(start=0):
    try: _write(start); return start
    except OSError as e: raise CounterError(str(e))