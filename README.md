# btcvol

Python package for building and testing Bitcoin implied volatility prediction models for CrunchDAO competitions.

[![PyPI version](https://badge.fury.io/py/btcvol.svg)](https://badge.fury.io/py/btcvol)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
# Install from GitHub
pip install git+https://github.com/jberros/btcvol-python.git

# Or from PyPI (coming soon)
pip install btcvol
```

## Quick Start

```python
from btcvol import TrackerBase, test_model_locally
from btcvol.examples import GARCHVolatilityModel
import numpy as np

# Option 1: Use the built-in GARCH model
model = GARCHVolatilityModel(base_vol=0.42)
predictions = model.predict("BTC", horizon=3600, step=900)
print(f"Generated {len(predictions)} predictions: {predictions}")

# Option 2: Create your own custom model
class MyVolatilityModel(TrackerBase):
    def predict(self, asset: str, horizon: int, step: int):
        """
        Generate volatility predictions.
        
        Args:
            asset: Asset to predict (e.g., "BTC")
            horizon: Time horizon in seconds (e.g., 3600 for 1h, 86400 for 24h)
            step: Prediction resolution in seconds (e.g., 900 for 15 min)
        
        Returns:
            List of predicted volatility values (0-1 range, e.g., 0.40 = 40%)
        """
        num_predictions = horizon // step
        base_vol = 0.42
        
        # Apply mean reversion based on horizon
        horizon_hours = horizon / 3600
        adjustment = 1.0 / np.sqrt(horizon_hours / 24.0)
        
        return [base_vol * adjustment] * num_predictions

# Test your model locally
if __name__ == "__main__":
    test_model_locally(MyVolatilityModel)
```

## Features

- **TrackerBase**: Abstract base class for building volatility prediction models
- **test_model_locally()**: Validate your model before submission
- **Example Models**: Pre-built models to help you get started
  - `GARCHVolatilityModel`: Mean-reverting GARCH-style predictions
  - `RandomWalkModel`: Random walk with configurable volatility
  - `LinearDecayModel`: Linear decay from start to end volatility

## Example Models

### GARCH-Style Model

```python
from btcvol.examples import GARCHVolatilityModel

model = GARCHVolatilityModel(base_vol=0.42)
predictions = model.predict("BTC", horizon=3600, step=900)
# Returns 4 predictions for 1-hour horizon with 15-min steps
```

### Custom Model

```python
import numpy as np
from btcvol import TrackerBase

class AdvancedModel(TrackerBase):
    def __init__(self):
        super().__init__()
        # Initialize your model parameters
        
    def predict(self, asset: str, horizon: int, step: int):
        num_predictions = horizon // step
        # Your sophisticated prediction logic here
        return [0.40] * num_predictions
```

## Competition Details

This package is designed for CrunchDAO's Bitcoin DVOL prediction competition:

- **Target**: Deribit 30-day Bitcoin Implied Volatility (DVOL)
- **Prediction Frequency**: Every 15 minutes
- **Horizons**: 1 hour (3600s) and 24 hours (86400s)
- **Evaluation**: Mean Squared Error (MSE) over 30-day period

## Testing Your Model

```python
from btcvol import test_model_locally
from your_module import YourModel

# Run validation tests
test_model_locally(YourModel)
```

The test validates:
- ✓ Model inherits from TrackerBase
- ✓ Predict method is implemented
- ✓ Returns correct number of predictions
- ✓ All predictions are numeric
- ✓ Values are in reasonable range

## API Reference

### TrackerBase

Base class for all volatility prediction models.

**Methods:**
- `predict(asset, horizon, step)` - **[Abstract]** Generate predictions
- `fetch_price_data(asset, days)` - Helper to fetch historical prices
- `fetch_dvol_data(days)` - Helper to fetch historical DVOL data

### test_model_locally(model_class, verbose=True)

Validate your model implementation.

**Parameters:**
- `model_class`: Your model class (not an instance)
- `verbose`: Print detailed test results

**Returns:**
- `bool`: True if all tests pass

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/btcvol-python.git
cd btcvol-python

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Requirements

- Python >= 3.9
- pandas >= 2.0.0
- numpy >= 1.24.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **Competition Platform**: [CrunchDAO](https://www.crunchdao.com/)
- **Documentation**: [Full Docs](https://github.com/yourusername/btcvol-python/docs)
- **Issue Tracker**: [GitHub Issues](https://github.com/yourusername/btcvol-python/issues)

## Support

For competition-specific questions, visit the [CrunchDAO Discord](https://discord.gg/crunchdao).

For package issues, please [open an issue](https://github.com/yourusername/btcvol-python/issues) on GitHub.
