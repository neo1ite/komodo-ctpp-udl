# Komodo CTPP UDL

[Русский](docs/i18n/README.ru.md) | **English**

This extension adds **CTPP2 / CT++** template support to Komodo IDE and Komodo Edit.

It registers the `CTPP` language for `*.ctpp` files, provides syntax highlighting for mixed CTPP/HTML5/CSS/JavaScript templates, supports Underscore templates, linting, and Code Intelligence integration.

## Features

- dedicated `CTPP` language in Komodo;
- syntax highlighting for `*.ctpp` files;
- HTML5, CSS and JavaScript sublanguages inside templates;
- CTPP highlighting inside HTML attributes, `<script>` attributes and JavaScript strings;
- Underscore template highlighting in HTML and JavaScript contexts;
- HTML5-based linting with CTPP sanitizing;
- **Code Intelligence 2.0:** CTPP language registration in CodeIntel and autocomplete for `TMPL_*` tags;
- native HTML5, CSS and JavaScript CodeIntel delegation inside mixed CTPP documents;
- CTPP file templates;
- dedicated CTPP icon for files and language UI;
- compatibility with Komodo IDE and Komodo Edit versions 6–9.

Further CodeIntel stages (expressions, CILE, Go to Definition, variables, Code Browser/project index) are tracked in [the CodeIntel roadmap](docs/CODEINTEL.ru.md).

## Installation

Install the XPI using Komodo's Add-ons manager.

After updating a development build, fully close Komodo and clear its startup cache:

```bash
rm -rf ~/.komodoide/9.3/XRE/startupCache
```

For CodeIntel changes it is also useful to restart Komodo completely so that the CodeIntel backend process is recreated.

## Building

Komodo 9 ships with its own Python 2.7 runtime, `mozpython`. On modern Linux systems the generic `python` command may be absent, so build through Komodo's runtime.

**Important:** use `--unjarred`. The extension registers `content/`, `skin/` and `locale/` through chrome URLs.

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    "$KOMODO_HOME/lib/sdk/bin/koext" build --unjarred
```

A successful version 2.0.1 build creates:

```text
ctpp_language-2.0.1-ko.xpi
```

The build output must contain top-level `skin/` and `content/` directories and must **not** contain `ctpp_language.jar`.

## Code Intelligence 2.0

Version 2.0 introduced the first functional CTPP CodeIntel layer:

- explicit `LangInfo` registration for `CTPP`;
- `TPL_*`-based CodeIntel instead of the old generated `SSL_*` stub;
- automatic `TMPL_*` tag completion after `<TMPL_` and after two characters of a tag name;
- explicit completion (`Ctrl+J`) for a partially typed `TMPL_*` tag;
- container-tag completion for closing forms such as `</TMPL_...>`;
- HTML5/XML completion in markup areas;
- JavaScript and CSS CodeIntel/CILE delegation in their respective UDL families.

Version 2.0.1 is a release-engineering hotfix: it fixes `patch-komodo-codeintel.sh uninstall` when install and uninstall happen within the same filesystem timestamp interval, and marks the build/patch scripts executable. CTPP CodeIntel semantics are unchanged.

Expression completion is intentionally deferred to version 2.1.

### Komodo 9 autocomplete retrigger patch

Komodo 9 has an early return in `ko.codeintel.trigger()` when an autocomplete popup is already open. HTML5 opens its tag popup after `<`, so the core refuses to calculate the new CTPP trigger when LexUDL later switches from the markup (`M`) family to the template (`TPL`) family at `<TMPL_`.

The repository contains an idempotent patch manager for this Komodo 9 behaviour:

```bash
# Komodo must be fully closed for install/uninstall.
./patch-komodo-codeintel.sh status
./patch-komodo-codeintel.sh install
./patch-komodo-codeintel.sh status

# Re-running install is a no-op.
./patch-komodo-codeintel.sh install

# Roll back only this patch; re-running uninstall is also a no-op.
./patch-komodo-codeintel.sh uninstall
./patch-komodo-codeintel.sh uninstall
```

The script:

- defaults to `$HOME/Komodo-IDE-9` and can be redirected with `KOMODO_HOME`;
- modifies only `content/codeintel/codeintel.js` inside `lib/mozilla/chrome/komodo.jar`;
- refuses to patch an unknown/incompatible CodeIntel implementation;
- keeps the original JavaScript entry in `lib/mozilla/chrome/.ctpp-codeintel-patch/`;
- never overwrites that original backup on repeated installs;
- replaces the target JAR entry deterministically instead of relying on ZIP timestamp-based `-u` behaviour;
- performs JAR replacement through a verified temporary copy;
- is idempotent for both `install` and `uninstall`;
- clears the Komodo startup cache after install/uninstall.

A raw unified diff of the core change is also stored in `patches/komodo-9-codeintel-autocomplete-retrigger.patch` for review.

## Language icon

CTPP file/tab icons are resolved through Komodo's file-icon machinery. The language selector is a different UI path: Komodo creates menu items with class `languageicon` and the attribute `language="CTPP"`.

The extension injects the CTPP language CSS directly into the main Komodo chrome.

## Project structure

- `udl/` — UDL definitions and language-family transitions;
- `components/` — language registration and linter components;
- `pylib/` — Code Intelligence, LangInfo and future CILE integration;
- `patches/` — reference patches for Komodo 9 itself;
- `patch-komodo-codeintel.sh` — idempotent Komodo 9 CodeIntel patch manager;
- `templates/` — new-file templates;
- `skin/` — UI resources, including `languages.css` and `ctpp.svg`.

## Compatibility

Primary tested configuration:

- Komodo IDE 9.3.2 build 88191;
- Linux x86_64.

`install.rdf` allows Komodo IDE and Komodo Edit versions 6–9.

## Diagnostics

If a newly installed development build is not reflected in the UI, close Komodo and remove:

```text
~/.komodoide/9.3/XRE/startupCache
```

Then start Komodo again.

If the old CodeIntel state remains after installing 2.0/2.0.1, fully terminate all Komodo processes before restarting the IDE. CodeIntel runs in a separate backend process and must reload extension `pylib/` modules.

Check the Komodo core patch independently with:

```bash
./patch-komodo-codeintel.sh status
```

## License

MIT License. See [LICENSE](LICENSE).
