# Recolector de colas - PortAventura

Recolecta cada 10 minutos el tiempo de espera de todas las atracciones
de PortAventura Park (via la API publica de queue-times.com) y lo
guarda en `data/history.jsonl`, usando GitHub Actions como recolector
gratuito en la nube (no requiere dejar ningun ordenador encendido).

## Como activarlo

1. Sube este contenido tal cual a un repositorio de GitHub (puede ser
   publico o privado, ver nota mas abajo).
2. Ve a la pestaña "Actions" del repositorio. El workflow
   "Recolectar colas PortAventura" deberia aparecer listo.
3. Se ejecutara solo cada 10 minutos a partir de ese momento. Tambien
   puedes forzar una ejecucion manual con el boton "Run workflow".

## Nota sobre repos publicos vs privados

- **Publico**: minutos de GitHub Actions ilimitados y gratis, pero
  el historico de colas queda visible para cualquiera.
- **Privado**: 2000 minutos gratis/mes, mas que suficiente para un
  intervalo de 10 min, pero los datos no son visibles publicamente.

## Recuperar los datos acumulados

Cuando quieras usarlos (por ejemplo para entrenar un modelo), haz
`git pull` de este repositorio o descarga directamente
`data/history.jsonl` desde la web de GitHub.
