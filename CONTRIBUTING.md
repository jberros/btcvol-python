# btcvol-python

Standalone Python package for CrunchDAO's Bitcoin DVOL prediction competition.

## Repository Structure

```
btcvol-python/
├── btcvol/               # Main package
│   ├── __init__.py
│   ├── tracker.py        # TrackerBase class
│   ├── testing.py        # test_model_locally()
│   └── examples.py       # Example models
├── tests/                # Unit tests
│   ├── __init__.py
│   └── test_btcvol.py
├── README.md             # Package documentation
├── LICENSE               # MIT License
├── setup.py              # Package setup (legacy)
├── pyproject.toml        # Modern package configuration
├── MANIFEST.in           # Package manifest
└── .gitignore
```

## Quick Start

1. **Install locally for development:**
   ```bash
   pip install -e .
   ```

2. **Run tests:**
   ```bash
   pytest tests/
   ```

3. **Build package:**
   ```bash
   python -m build
   ```

4. **Upload to PyPI:**
   ```bash
   # Test PyPI first
   twine upload --repository testpypi dist/*
   
   # Production PyPI
   twine upload dist/*
   ```

## Development

Make changes to the `btcvol/` directory, then test:

```bash
# Install in editable mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Format code
black btcvol/ tests/

# Lint
flake8 btcvol/ tests/
```

## Publishing to PyPI

1. Update version in `setup.py` and `pyproject.toml`
2. Build: `python -m build`
3. Upload: `twine upload dist/*`

## Links

- PyPI: https://pypi.org/project/btcvol/
- Competition: https://www.crunchdao.com/
- Main Repo: https://github.com/yourusername/btc-dvol-competition
