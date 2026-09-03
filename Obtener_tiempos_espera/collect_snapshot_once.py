"""
Version de UN SOLO SNAPSHOT del recolector, para ejecutar en GitHub
Actions (o cualquier entorno donde no puedas dejar un proceso corriendo
indefinidamente). Hace una llamada a la API, guarda el resultado, y
termina. El propio workflow de GitHub Actions es quien se encarga de
volver a lanzarlo cada X minutos.

Guarda en formato JSONL (un JSON por linea) en vez de SQLite, porque
Git compara y almacena texto plano de forma mucho mas eficiente que
binarios: cada commit solo añade las lineas nuevas, en vez de guardar
una copia completa del fichero cada vez.

Uso:
    python3 collect_snapshot_once.py
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import requests

PARK_ID = 19  # PortAventura Park en queue-times.com
API_URL = f"https://queue-times.com/parks/{PARK_ID}/queue_times.json"

DATA_DIR = Path(__file__).parent / "data"
HISTORY_FILE = DATA_DIR / "history.jsonl"


def fetch_snapshot() -> list[dict]:
    resp = requests.get(API_URL, timeout=15)
    resp.raise_for_status()
    raw = resp.json()

    rides = []
    for land in raw.get("lands", []):
        rides.extend(land.get("rides", []))
    rides.extend(raw.get("rides", []))
    return rides


def main():
    DATA_DIR.mkdir(exist_ok=True)

    rides = fetch_snapshot()
    ahora = datetime.now(timezone.utc)

    lineas = []
    for r in rides:
        lineas.append(json.dumps({
            "atraccion": r["name"],
            "timestamp_utc": ahora.isoformat(),
            "fecha": ahora.strftime("%Y-%m-%d"),
            "hora": ahora.strftime("%H:%M:%S"),
            "dia_semana": ahora.weekday(),
            "mes": ahora.month,
            "minuto_del_dia": ahora.hour * 60 + ahora.minute,
            "wait_time": r["wait_time"],
            "is_open": r["is_open"],
        }, ensure_ascii=False))

    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"Guardadas {len(lineas)} filas ({ahora.isoformat()}).")


if __name__ == "__main__":
    main()
