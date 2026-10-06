# todofind

Stdlib-only Python CLI that finds TODO/FIXME/HACK/XXX comments in a directory tree.
Useful for quick audits and CI gates. Skips `.git`, `node_modules` and binary files.

## Install

No dependencies (Python 3.8+). Run from a checkout: `python -m todofind`.

## Usage

```
python -m todofind [path] [--tag TAG]... [--json] [--fail]
python -m todofind src                 # file:line: TAG text
python -m todofind --tag todo --tag fixme
python -m todofind --json > todos.json
python -m todofind --fail              # exit 1 if any found (CI)
```

Example output: `src/app.py:12: TODO handle errors`

## Tests

`python -m unittest`

## License

MIT
