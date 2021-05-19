# Fast Cards
[![Tests](https://github.com/dRacz3/fast-cards/actions/workflows/main.yml/badge.svg)](https://github.com/dRacz3/fast-cards/actions/workflows/main.yml)
[![deepcode](https://www.deepcode.ai/api/gh/badge?key=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwbGF0Zm9ybTEiOiJnaCIsIm93bmVyMSI6ImRSYWN6MyIsInJlcG8xIjoiZmFzdC1jYXJkcyIsImluY2x1ZGVMaW50IjpmYWxzZSwiYXV0aG9ySWQiOjE1ODk3LCJpYXQiOjE2MjA4NDg4ODl9.7e8j9KNMQV0TQJkXmMOlLG16iEKP5pgZo099Xp-98O4)](https://www.deepcode.ai/app/gh/dRacz3/fast-cards/_/dashboard?utm_content=gh%2FdRacz3%2Ffast-cards)
[![CodeQL](https://github.com/dRacz3/fast-cards/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/dRacz3/fast-cards/actions/workflows/codeql-analysis.yml)


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
