# CTPP language support for Komodo

**English** | [Русский](docs/i18n/README.ru.md)

This extension adds **CTPP2 / CT++** template support to Komodo IDE and Komodo Edit.

It registers the `CTPP` language for `*.ctpp` files, provides syntax highlighting for mixed CTPP/HTML5/CSS/JavaScript templates, and includes UDL support used by the project for Underscore templates.

## Features

- dedicated `CTPP` language in Komodo;
- syntax highlighting for `*.ctpp` files;
- HTML5, CSS and JavaScript sublanguages inside templates;
- CTPP file templates;
- linter and Code Intelligence/CILE integration components;
- dedicated CTPP icon for files and language UI;
- compatibility with Komodo IDE and Komodo Edit versions 6–9.

Full modern Code Intelligence for CTPP is not implemented yet.

## Installation

Install the XPI package through Komodo's Add-ons Manager.

After updating a development build, fully close Komodo and clear its startup cache before starting it again:

```bash
rm -rf ~/.komodoide/9.3/XRE/startupCache
```

## Building

Komodo 9 ships with its own Python 2.7 runtime, `mozpython`. On modern Linux systems the generic `python` command may be absent, so build through Komodo's runtime.

**Important:** use `--unjarred`. Komodo SDK otherwise packs `content/`, `skin/` and `locale/` into `ctpp_language.jar`, while this extension's chrome manifest addresses `chrome://ctpp/skin/languages.css` and `ctpp.svg` as ordinary chrome directories. The language-menu icon therefore requires the unjarred build.

```bash
KOMODO_HOME="${KOMODO_HOME:-$HOME/Komodo-IDE-9}"

"$KOMODO_HOME/lib/mozilla/mozpython" \
    "$KOMODO_HOME/lib/sdk/bin/koext" build --unjarred
```

A successful version 1.3 build creates:

```text
ctpp_language-1.3-ko.xpi
```

The build output must contain top-level `skin/` and `content/` directories and must **not** contain `ctpp_language.jar`.

## Language icon

CTPP file/tab icons are resolved through Komodo's file-icon machinery. The language selector is a different UI path: Komodo creates menu items with class `languageicon` and the attribute `language="CTPP"`.

Version 1.3 injects the CTPP language CSS directly into the main Komodo chrome:

```text
style chrome://komodo/content/komodo.xul chrome://ctpp/skin/languages.css
```

The stylesheet overrides the language-menu image for `language="CTPP"`; the SVG itself is stored in `skin/ctpp.svg`.

The XPI must be built with `koext build --unjarred`, otherwise Komodo SDK places the skin inside a JAR and the chrome URL above does not resolve to the packaged stylesheet as intended.

## Project layout

- `udl/` — UDL definitions and language-family transitions;
- `components/` — language registration and linter components;
- `pylib/` — Code Intelligence/CILE integration;
- `templates/` — new-file templates;
- `skin/` — UI resources, including `languages.css` and `ctpp.svg`;
- `content/` — other chrome resources when needed.

## Compatibility

Primary tested configuration:

- Komodo IDE 9.3.2 build 88191;
- Linux x86_64.

`install.rdf` allows Komodo IDE and Komodo Edit versions 6 through 9.

## Troubleshooting

If a newly installed development build is not reflected in the UI, close Komodo completely and remove:

```text
~/.komodoide/9.3/XRE/startupCache
```

Then start Komodo again.

If Code Intelligence reports an exception while scanning an unrelated JavaScript file, that is separate from CTPP language registration and should be diagnosed independently.

## License

MIT License. See [LICENSE](LICENSE).
