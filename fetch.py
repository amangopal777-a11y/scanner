import json, os, sys, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
UA = {"User-Agent": "Mozilla/5.0"}
os.makedirs("data", exist_ok=True)
syms = [l.strip() for l in open("symbols.txt") if l.strip() and not l.startswith("#")]

def get(sym):
    for attempt in range(3):
        for host in ("query1", "query2"):
            try:
                u = f"https://{host}.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(sym)}?range=3mo&interval=1d"
                j = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20))
                r = j["chart"]["result"][0]
                q = r["indicators"]["quote"][0]
                keep = [i for i, t in enumerate(r["timestamp"]) if q["close"][i] is not None and q["high"][i] is not None and q["low"][i] is not None]
                m = r["meta"]
                out = {"chart": {"result": [{
                    "meta": {"regularMarketPrice": m.get("regularMarketPrice"), "shortName": m.get("shortName"), "longName": m.get("longName"),
                             "currentTradingPeriod": {"regular": m.get("currentTradingPeriod", {}).get("regular", {})}},
                    "timestamp": [r["timestamp"][i] for i in keep],
                    "indicators": {"quote": [{k: [round(q[k][i], 2) for i in keep] for k in ("high", "low", "close")}]}}], "error": None}}
                open("data/" + sym.replace("^", "_") + ".json", "w").write(json.dumps(out, separators=(",", ":")))
                return True
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(4 * (attempt + 1))
            except Exception:
                pass
        time.sleep(1)
    print("failed:", sym)
    return False

with ThreadPoolExecutor(max_workers=5) as ex:
    ok = sum(ex.map(get, syms))
print(ok, "of", len(syms), "saved")
sys.exit(0 if ok >= len(syms) * 0.5 else 1)
