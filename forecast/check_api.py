"""Call every API endpoint once (in-process, no server needed) and report what came back.

    .venv/bin/python -m forecast.check_api
"""
from __future__ import annotations

import sys

from fastapi.testclient import TestClient

from .api import app


def main() -> None:
    c = TestClient(app)
    m = c.get("/api/forecast/measurements").json()
    last = c.get("/api/forecast/observations/latest").json()["time"]
    day = last[:10]
    calls = [
        ("/api/forecast/measurements", None),
        ("/api/forecast/observations/latest", None),
        ("/api/forecast/observations", {"variable": "speed_km_s", "start": day, "end": last}),
        ("/api/forecast/predictions", {"variable": "sym_h_nT", "horizon": "1 h", "start": day, "end": last}),
        ("/api/forecast/events/outlook", None),
        ("/api/forecast/events/history", {"min_severity": "Intense"}),
        ("/api/forecast/events/unusual", {"days": 30}),
        ("/api/forecast/models/performance", None),
        ("/api/forecast/day", {"date": "2024-05-11"}),
        ("/api/forecast/day", {"date": "2026-11-08"}),
        ("/api/forecast/day", {"date": "2031-07-01"}),
        ("/api/forecast/dataset", None),
        ("/api/forecast/predictions", {"variable": "nope", "horizon": "1 h", "start": day, "end": last}),
    ]
    bad = 0
    for path, params in calls:
        r = c.get(path, params=params)
        body = r.json()
        size = {k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in body.items()} if isinstance(body, dict) else body
        expect = 404 if params and params.get("variable") == "nope" else 200
        ok = r.status_code == expect
        bad += not ok
        print(f"{'OK ' if ok else 'BAD'} {r.status_code} {path} {params or ''}\n     {str(size)[:220]}")
    print(f"{len(m['measurements'])} measurements, horizons {m['horizons']}")
    print(f"{len(calls) - bad} of {len(calls)} calls answered as expected.")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
