"""
Obtiene los tiempos de cola actuales de PortAventura Park usando la API
publica de queue-times.com y los guarda en data/queue_times.json

API docs: https://queue-times.com/en-US/pages/api
Park ID de PortAventura Park: 19
"""

import json
import requests
from datetime import datetime, timezone
from pathlib import Path

PARK_ID = 19  # PortAventura Park (queue-times.com)
API_URL = f"https://queue-times.com/parks/{PARK_ID}/queue_times.json"

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_FILE = DATA_DIR / "queue_times.json"


def fetch_queue_times() -> dict:
    """Llama a la API y devuelve el JSON crudo."""
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()


def flatten_rides(raw: dict) -> list[dict]:
    """
    Convierte la estructura anidada por 'lands' en una lista plana de
    atracciones: [{name, land, wait_time, is_open, last_updated}, ...]
    Incluye tambien las rides que no estan agrupadas en ningun land
    (algunos parques las devuelven sueltas en raw['rides']).
    """
    rides = []

    for land in raw.get("lands", []):
        land_name = land.get("name", "Sin zona")
        for ride in land.get("rides", []):
            rides.append({
                "name": ride["name"],
                "land": land_name,
                "wait_time": ride["wait_time"],
                "is_open": ride["is_open"],
                "last_updated": ride.get("last_updated"),
            })

    # Algunos parques devuelven rides sueltas fuera de 'lands'
    for ride in raw.get("rides", []):
        rides.append({
            "name": ride["name"],
            "land": "Sin zona",
            "wait_time": ride["wait_time"],
            "is_open": ride["is_open"],
            "last_updated": ride.get("last_updated"),
        })

    return rides


def main():
    DATA_DIR.mkdir(exist_ok=True)

    raw = fetch_queue_times()
    rides = flatten_rides(raw)

    result = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "park_id": PARK_ID,
        "rides": rides,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # --- Salida en consola para verlo rapido ---
    print(f"\nAtracciones de PortAventura Park ({len(rides)} encontradas)\n")
    print(f"{'Atraccion':<35} {'Zona':<25} {'Cola':>6}  Abierta")
    print("-" * 80)
    for r in sorted(rides, key=lambda x: x["name"]):
        estado = "Si" if r["is_open"] else "No"
        print(f"{r['name']:<35} {r['land']:<25} {r['wait_time']:>4} min  {estado}")

    print(f"\nGuardado en: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
