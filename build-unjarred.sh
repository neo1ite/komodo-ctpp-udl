#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
KOMODO_HOME=${KOMODO_HOME:-"$HOME/Komodo-IDE-9"}

cd "$ROOT"
exec "$KOMODO_HOME/lib/mozilla/mozpython" \
    "$KOMODO_HOME/lib/sdk/bin/koext" build --unjarred "$@"
