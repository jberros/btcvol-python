"""
BTC DVOL Competition - Participant Package

This package provides the essential tools for participants to develop and test
their Bitcoin implied volatility prediction models locally before submission.
"""

from .tracker import TrackerBase
from .testing import test_model_locally

__version__ = "1.0.0"
__all__ = ["TrackerBase", "test_model_locally"]
