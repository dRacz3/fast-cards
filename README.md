# Fast Cards
[![Tests](https://github.com/dRacz3/fast-cards/actions/workflows/main.yml/badge.svg)](https://github.com/dRacz3/fast-cards/actions/workflows/main.yml)


# Project setup using poetry:
## prerequisites:
- python 3.9+ installed
- poetry installed (https://python-poetry.org/)
```bash
poetry shell
poetry install
```
## Activate virtualenv:
```bash
poetry shell
```
After this, you can run:

### Linter and tests:
```bash
make lnf
```

### The application server:
```bash
PYTHONPATH=. RUNTIME_ENV='PROD' python src/main.py
```

Note: not specifying `RUNTIME_ENV` whill default back to `TEST`, which is the only value handled differently. Providing anything else will trigger the production setup.
