#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"
MOZPYTHON="${MOZPYTHON:-$KOMODO_HOME/lib/mozilla/mozpython}"
KOMODO_PYTHON="$KOMODO_HOME/lib/mozilla/python"
KOMODO_PYTHON_KOMODO="$KOMODO_PYTHON/komodo"

if [ ! -x "$MOZPYTHON" ]; then
    echo "mozpython not found or not executable: $MOZPYTHON" >&2
    exit 1
fi

if [ ! -f "$KOMODO_PYTHON_KOMODO/codeintel2/manager.py" ]; then
    echo "codeintel2/manager.py not found under: $KOMODO_PYTHON_KOMODO" >&2
    exit 1
fi

if [ ! -f "$ROOT_DIR/build/lexers/CTPP.lexres" ]; then
    echo "build/lexers/CTPP.lexres not found; run ./build.sh first" >&2
    exit 1
fi

# Standalone mozpython does not inherit the same sys.path that the running
# Komodo application prepares. Add both Komodo Python roots explicitly.
if [ -n "${PYTHONPATH:-}" ]; then
    PYTHONPATH="$KOMODO_PYTHON_KOMODO:$KOMODO_PYTHON:$PYTHONPATH"
else
    PYTHONPATH="$KOMODO_PYTHON_KOMODO:$KOMODO_PYTHON"
fi
export PYTHONPATH
export KOMODO_HOME

exec "$MOZPYTHON" "$ROOT_DIR/tests/cile-mixed-smoke.py"
