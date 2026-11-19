import json, os, sys, time, urllib.parse, urllib.request
UA = {"User-Agent": "Mozilla/5.0"}
os.makedirs("data", exist_ok=True)
syms = [l.strip() for l in open("symbols.txt") if l.strip() and not l.startswith("#")]
ok = 0
for s in syms:
    for host in ("query1", "query2"):
        try:
            u = f"https://{host}.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(s)}?range=6mo&interval=1d"
            j = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20))
            if j.get("chart", {}).get("result"):
                json.dump(j, open("data/" + s.replace("^", "_") + ".json", "w"))
                ok += 1
                break
        except Exception as e:
            print(s, host, e)
    time.sleep(0.5)
print(ok, "of", len(syms), "saved")
sys.exit(0 if ok else 1)
