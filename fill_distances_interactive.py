"""
Flujo completo e interactivo para rellenar data/pares_a_rellenar.csv:

- Si el CSV no existe: lo crea con todas las parejas (metros vacio).
- Si existe y esta completo: avisa y no hace nada.
- Si existe y esta a medias: retoma justo donde lo dejaste, abriendo en
  el navegador la ruta a pie de Google Maps para cada pareja pendiente,
  una a una. Tu escribes los metros en la terminal y pulsas Enter.
  CADA respuesta se guarda en el CSV al instante, asi que puedes cerrar
  el script (Ctrl+C, cerrar la terminal, 'salir') en cualquier momento
  sin perder lo ya introducido, y al volver a ejecutar continua donde
  lo dejaste.

Comandos durante el rellenado:
    <numero>   -> guarda esos metros y pasa a la siguiente pareja
    saltar     -> deja esta pareja vacia por ahora y pasa a la siguiente
    salir      -> para aqui (lo ya guardado se queda guardado)

Uso:
    python3 fill_distances_interactive.py
"""

import csv
import json
import webbrowser
from itertools import combinations
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
QUEUE_TIMES_FILE = DATA_DIR / "queue_times.json"
COORDINATES_FILE = DATA_DIR / "coordinates.json"
CSV_FILE = DATA_DIR / "pares_a_rellenar.csv"

FIELDNAMES = ["atraccion_1", "atraccion_2", "metros"]


def load_names() -> list[str]:
    with open(QUEUE_TIMES_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return sorted(r["name"] for r in data["rides"])


def load_coordinates() -> dict:
    """Si existe coordinates.json, lo usamos para abrir la ruta con
    coordenadas exactas en vez de solo el nombre (mas fiable)."""
    if not COORDINATES_FILE.exists():
        return {}
    with open(COORDINATES_FILE, encoding="utf-8") as f:
        return json.load(f)


def create_csv(names: list[str]) -> None:
    pares = list(combinations(names, 2))
    DATA_DIR.mkdir(exist_ok=True)
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for a, b in pares:
            writer.writerow({"atraccion_1": a, "atraccion_2": b, "metros": ""})
    print(f"Creado {CSV_FILE} con {len(pares)} parejas.")


def load_csv() -> list[dict]:
    with open(CSV_FILE, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_csv(rows: list[dict]) -> None:
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def build_maps_url(a: str, b: str, coordinates: dict) -> str:
    if a in coordinates and b in coordinates:
        origin = f"{coordinates[a]['lat']},{coordinates[a]['lng']}"
        destination = f"{coordinates[b]['lat']},{coordinates[b]['lng']}"
    else:
        # Fallback sin coordenadas: busqueda por texto
        origin = f"PortAventura {a}".replace(" ", "+")
        destination = f"PortAventura {b}".replace(" ", "+")
    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={origin}"
        f"&destination={destination}"
        "&travelmode=walking"
    )


def main():
    names = load_names()

    if not CSV_FILE.exists():
        create_csv(names)
        print("Vuelve a ejecutar el script para empezar a rellenar parejas.")
        return

    rows = load_csv()
    pendientes = sum(1 for r in rows if not r["metros"].strip())

    if pendientes == 0:
        print(f"✅ {CSV_FILE} ya esta completo ({len(rows)} parejas). No se hace nada.")
        return

    coordinates = load_coordinates()
    if not coordinates:
        print("⚠ No se encontro coordinates.json, se usara busqueda por texto en Maps")
        print("  (menos fiable que coordenadas exactas).\n")

    print(f"{pendientes} de {len(rows)} parejas pendientes.")
    print("Se abrira Google Maps con la ruta a pie de cada pareja.")
    print("Escribe los metros y Enter. 'saltar' para dejarla, 'salir' para parar.\n")

    for row in rows:
        if row["metros"].strip():
            continue  # ya rellenada (en esta sesion o en una anterior)

        a, b = row["atraccion_1"], row["atraccion_2"]
        url = build_maps_url(a, b, coordinates)
        webbrowser.open(url)

        while True:
            try:
                respuesta = input(f"{a}  <->  {b}   metros: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nInterrumpido. Lo ya guardado se queda guardado.")
                return

            if respuesta.lower() == "salir":
                print("\nProgreso guardado. Ejecuta el script otra vez para continuar.")
                return
            if respuesta.lower() == "saltar":
                break

            try:
                metros = float(respuesta.replace(",", "."))
            except ValueError:
                print("  No es un numero valido. Prueba de nuevo, o 'saltar' / 'salir'.")
                continue

            row["metros"] = str(metros)
            save_csv(rows)  # <-- se guarda AL INSTANTE, no al final
            break

    restantes = sum(1 for r in rows if not r["metros"].strip())
    if restantes == 0:
        print("\n🎉 Todas las parejas rellenadas. Ya puedes ejecutar parse_filled_pairs.py")
    else:
        print(f"\nQuedan {restantes} parejas pendientes (saltadas). Vuelve a ejecutar cuando quieras.")


if __name__ == "__main__":
    main()
