"""
Base class for BTC DVOL prediction models.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import pandas as pd


class TrackerBase(ABC):
    """
    Base class for Bitcoin implied volatility prediction models.
    
    Participants must implement the predict() method to generate volatility forecasts.
    
    Example:
        >>> class MyVolModel(TrackerBase):
        ...     def predict(self, asset: str, horizon: int, step: int) -> List[float]:
        ...         # Your prediction logic here
        ...         return [0.40, 0.39, 0.38, 0.37]  # Example predictions
    """
    
    def __init__(self):
        """Initialize the tracker."""
        pass
    
    @abstractmethod
    def predict(self, asset: str, horizon: int, step: int) -> List[float]:
        """
        Generate volatility predictions for the specified horizon.
        
        Args:
            asset: The asset to predict (always "BTC" in this competition)
            horizon: Time horizon in seconds (3600 for 1h, 86400 for 24h)
            step: Prediction resolution in seconds (900 = 15 minutes)
            
        Returns:
            List of predicted implied volatility values (one per step)
            Values should be in 0-1 range (e.g., 0.40 = 40% volatility)
            Must return exactly horizon // step predictions
            
        Example:
            For horizon=3600 (1 hour) and step=900 (15 min):
            Returns 4 predictions: [0.42, 0.41, 0.40, 0.39]
        
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement predict()")
    
    def fetch_price_data(self, asset: str = "BTC", days: int = 30) -> Optional[pd.DataFrame]:
        """
        Helper method to fetch historical price data.
        
        Note: This is a placeholder for local testing. In production, the competition
        infrastructure will provide real-time price data.
        
        Args:
            asset: Asset symbol (default: "BTC")
            days: Number of days of historical data to fetch
            
        Returns:
            DataFrame with columns: ['timestamp', 'price']
            Returns None if data unavailable
        """
        # This would be implemented in the actual competition environment
        # For local testing, participants should use public APIs
        return None
    
    def fetch_dvol_data(self, days: int = 30) -> Optional[pd.DataFrame]:
        """
        Helper method to fetch historical DVOL data.
        
        Note: This is a placeholder for local testing. Use Deribit API directly
        for historical data during development.
        
        Args:
            days: Number of days of historical data to fetch
            
        Returns:
            DataFrame with columns: ['timestamp', 'dvol']
            Returns None if data unavailable
        """
        # This would be implemented in the actual competition environment
        # For local testing, use: https://docs.deribit.com/#public-get_volatility_index_data
        return None
