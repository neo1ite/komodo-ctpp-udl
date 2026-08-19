#!/bin/sh
set -eu

KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"
MOZPYTHON="$KOMODO_HOME/lib/mozilla/mozpython"
KOEXT="$KOMODO_HOME/lib/sdk/bin/koext"

if [ ! -x "$MOZPYTHON" ]; then
    echo "mozpython not found: $MOZPYTHON" >&2
    exit 1
fi

if [ ! -f "$KOEXT" ]; then
    echo "koext not found: $KOEXT" >&2
    exit 1
fi

# chrome.manifest refers to content/, skin/ and locale/ as real extension
# directories.  koext jars these directories by default, which makes those
# relative chrome registrations invalid.  Keep chrome resources unjarred.
exec "$MOZPYTHON" "$KOEXT" build --unjarred "$@"
