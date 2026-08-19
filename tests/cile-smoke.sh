#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"
MOZPYTHON="${MOZPYTHON:-$KOMODO_HOME/lib/mozilla/mozpython}"
FIXTURE="$ROOT_DIR/tests/cile-basic.ctpp"

if [ ! -x "$MOZPYTHON" ]; then
    echo "mozpython not found or not executable: $MOZPYTHON" >&2
    exit 1
fi

TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT HUP INT TERM

"$MOZPYTHON" "$ROOT_DIR/pylib/cile_ctpp.py" "$FIXTURE" > "$TMP"

require() {
    pattern=$1
    if ! grep -Fq "$pattern" "$TMP"; then
        echo "CILE smoke test failed: missing: $pattern" >&2
        cat "$TMP" >&2
        exit 1
    fi
}

reject() {
    pattern=$1
    if grep -Fq "$pattern" "$TMP"; then
        echo "CILE smoke test failed: unexpected: $pattern" >&2
        cat "$TMP" >&2
        exit 1
    fi
}

require '<scope ilk="blob" lang="CTPP" name="cile-basic.ctpp"'
require '<scope ilk="function" name="card"'
require 'signature="TMPL_block &apos;card&apos; args(title, body)"'
require '<variable ilk="argument" name="title"'
require '<variable ilk="argument" name="body"'
require '__ctpp_include__'
require 'name="includes/header.ctpp"'
require '__ctpp_call__'
require 'name="dynamic_block"'
require '__dynamic__'
require '<scope ilk="function" name="comparison"'
reject 'ignored.ctpp'
reject 'name="ignored"'

printf '%s\n' "CILE smoke test: OK"
printf '%s\n' "runtime: $MOZPYTHON"
printf '%s\n' "fixture: $FIXTURE"
