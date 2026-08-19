# Komodo CTPP UDL

[Русский](docs/i18n/README.ru.md) | **English**

CTPP2 / CT++ support for Komodo IDE/Edit with mixed HTML5/CSS/JavaScript templates, linting and Code Intelligence.

- CTPP syntax highlighting, including HTML attributes and JavaScript strings.
- Mixed HTML5/CSS/JavaScript support.
- HTML5-based linting with CTPP sanitizing.
- Code Intelligence 2.0: `TMPL_*` completion.
- Code Intelligence 2.1: CT++ expressions, built-ins, operators, `foreach as`, `args(...)` and calltips.
- Idempotent Komodo 9 autocomplete patch manager.

Roadmap: [docs/CODEINTEL.ru.md](docs/CODEINTEL.ru.md).

## Building

```bash
./build.sh
```

Version 2.1 builds `ctpp_language-2.1-ko.xpi`. The full 2.1 acceptance matrix was verified on Komodo IDE 9.3.2 build 88191.

## License

MIT License. See [LICENSE](LICENSE).
