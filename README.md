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

Use the repository build script:

```bash
./build.sh
```

By default it uses `~/Komodo-IDE-9`. Override the installation directory when necessary:

```bash
KOMODO_HOME=/opt/Komodo-IDE-9 ./build.sh
```

The script runs Komodo's own Python 2.7 runtime and SDK:

```text
mozpython koext build --unjarred
```

`--unjarred` is intentional and required. Komodo SDK normally moves `content/`, `skin/` and `locale/` into `ctpp_language.jar`, while this extension's chrome manifest addresses these resources as normal extension directories. An unjarred build keeps the chrome registrations and the language-icon stylesheet reachable.

A successful version 1.3 build creates:

```text
ctpp_language-1.3-ko.xpi
```

## Language icon

Komodo 9 builds the Languages menu dynamically and gives each language item the `languageicon` class plus a `language` attribute. The extension provides `skin/languages.css`, which overrides the icon for `language="CTPP"` with `skin/ctpp.svg`.

The stylesheet is loaded globally through the same `agent-style-sheets` mechanism used by the working TypeScript extension:

```text
category agent-style-sheets ctpp-language-icons chrome://ctpp/skin/languages.css
```

The chrome resources must therefore remain reachable in the installed XPI; this is why the supported build uses `--unjarred`.

## Project layout

- `udl/` — UDL definitions and language-family transitions;
- `components/` — language registration and linter components;
- `pylib/` — Code Intelligence/CILE integration;
- `templates/` — new-file templates;
- `skin/` — UI resources, including `languages.css` and `ctpp.svg`;
- `content/` — other chrome resources when needed;
- `build.sh` — supported Komodo 9 build command.

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

For icon problems, verify that the built XPI contains `skin/languages.css` and `skin/ctpp.svg` as top-level directories rather than only inside `ctpp_language.jar`:

```bash
unzip -l ctpp_language-1.3-ko.xpi | grep -E 'skin/(languages\.css|ctpp\.svg)|ctpp_language\.jar'
```

## License

MIT License. See [LICENSE](LICENSE).
