#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"
MOZPYTHON="${MOZPYTHON:-$KOMODO_HOME/lib/mozilla/mozpython}"

if [ ! -x "$MOZPYTHON" ]; then
    echo "mozpython not found or not executable: $MOZPYTHON" >&2
    exit 1
fi

if [ ! -f "$ROOT_DIR/build/lexers/CTPP.lexres" ]; then
    echo "build/lexers/CTPP.lexres not found; run ./build.sh first" >&2
    exit 1
fi

exec "$MOZPYTHON" "$ROOT_DIR/tests/cile-mixed-smoke.py"
