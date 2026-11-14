"""
Smart Rotation Engine - Web Server & REST API.
Zero external server dependencies (uses Python built-in http.server).
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.engine import SmartRotationEngine, FarmerConstraints

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
engine = SmartRotationEngine()

class SmartRotationHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/evaluate":
            self.handle_evaluate_get()
        elif path == "/api/satellite-series":
            self.handle_satellite_series()
        elif path == "/api/crops":
            self.handle_crops()
        elif path == "/api/soil":
            self.handle_soil()
        else:
            # Fallback to static files
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/evaluate":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {}
            self.handle_evaluate(data)
        else:
            self.send_error(404, "Endpoint not found")

    def handle_evaluate_get(self):
        res = engine.evaluate(FarmerConstraints())
        self._send_json(res)

    def handle_evaluate(self, data: dict):
        constraints = FarmerConstraints(
            has_no_till_drill=data.get("has_no_till_drill", True),
            has_row_crop_planter=data.get("has_row_crop_planter", True),
            has_combine_grain_head=data.get("has_combine_grain_head", True),
            has_combine_corn_head=data.get("has_combine_corn_head", True),
            budget_limit_per_ha_usd=float(data.get("budget_limit_per_ha_usd", 650.0)),
            irrigation_available=data.get("irrigation_available", False),
            priority_yield_weight=float(data.get("priority_yield_weight", 0.35)),
            priority_water_weight=float(data.get("priority_water_weight", 0.20)),
            priority_soil_weight=float(data.get("priority_soil_weight", 0.30)),
            priority_cost_weight=float(data.get("priority_cost_weight", 0.15))
        )
        res = engine.evaluate(constraints)
        self._send_json(res)

    def handle_satellite_series(self):
        self._send_json({"series": engine.satellite_series})

    def handle_crops(self):
        crops_dict = {k: v.__dict__ for k, v in engine.crops.items()}
        self._send_json(crops_dict)

    def handle_soil(self):
        self._send_json(engine.soil.__dict__)

    def _send_json(self, payload: dict, status: int = 200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

def start_server(port: int = 8000):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, SmartRotationHandler)
    print(f"\n[+] Smart Rotation Engine Web Dashboard running at:")
    print(f"    http://127.0.0.1:{port}")
    print("    Press Ctrl+C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    start_server(port)
