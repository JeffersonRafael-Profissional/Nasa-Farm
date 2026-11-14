"""
Script to fetch agroclimatology data from NASA POWER API for Ames, Iowa.
Coordinates: Lat 42.0308, Lon -93.6319
Parameters:
  - T2M: Temperature at 2 Meters (C)
  - T2M_MAX: Maximum Temperature (C)
  - T2M_MIN: Minimum Temperature (C)
  - PRECTOTCORR: Corrected Precipitation (mm/day)
  - ALLSKY_SFC_SW_DWN: All Sky Surface Shortwave Downward Irradiance (MJ/m^2/day)
  - RH2M: Relative Humidity at 2 Meters (%)
  - GWETROOT: Root Zone Soil Wetness (0-1)
  - GWETTOP: Surface Soil Wetness (0-1)
"""

import os
import json
import urllib.request
import urllib.error
import csv

def fetch_nasa_power():
    lat = 42.0308
    lon = -93.6319
    start_date = "20240101"
    end_date = "20241231"
    
    parameters = "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,ALLSKY_SFC_SW_DWN,RH2M,GWETROOT,GWETTOP"
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"parameters={parameters}&community=AG&longitude={lon}&latitude={lat}&"
        f"start={start_date}&end={end_date}&format=JSON"
    )
    
    out_dir = os.path.join(os.path.dirname(__file__), "..", "Data")
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "nasa_power_ames_iowa_daily.json")
    csv_path = os.path.join(out_dir, "nasa_power_ames_iowa_daily.csv")
    
    print(f"Fetching from NASA POWER API:\n{url}")
    headers = {"User-Agent": "NasaSpaceApps2026/SmartRotationEngine"}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"Saved raw JSON to {json_path}")
            
            # Export to CSV as well
            props = data.get("properties", {}).get("parameter", {})
            dates = sorted(list(props.get("T2M", {}).keys()))
            
            param_names = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN", "RH2M", "GWETROOT", "GWETTOP"]
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["date"] + param_names)
                for d in dates:
                    row = [d] + [props.get(p, {}).get(d, "") for p in param_names]
                    writer.writerow(row)
            print(f"Saved CSV with {len(dates)} daily records to {csv_path}")
            return True
    except Exception as e:
        print(f"Error fetching NASA POWER data: {e}")
        return False

if __name__ == "__main__":
    fetch_nasa_power()
