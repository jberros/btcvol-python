"""
Base class for BTC DVOL prediction models.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Tuple
import pandas as pd
from datetime import datetime


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
    
    # Maximum number of rows to keep in price/DVOL cache (prevent RAM issues)
    MAX_CACHE_ROWS = 10000
    
    def __init__(self):
        """Initialize the tracker."""
        self._price_cache = {}
        self._dvol_cache = {}
    
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
    
    def fetch_price_data(
        self, 
        asset: str, 
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch historical price data from the competition infrastructure.
        
        This method is automatically called by the orchestrator during the tick() phase
        to provide models with price history. Models can access this data for training
        or feature engineering.
        
        Args:
            asset: Asset symbol (e.g., "BTC")
            from_timestamp: Start time for historical data (optional)
            to_timestamp: End time for historical data (optional)
            
        Returns:
            DataFrame with columns: ['timestamp', 'price']
            Empty DataFrame if no data available
            
        Note:
            In competition environment, this data is injected via tick() calls.
            For local testing, this returns cached data or empty DataFrame.
        """
        if asset in self._price_cache:
            df = self._price_cache[asset]
            if from_timestamp and to_timestamp:
                df = df[(df['timestamp'] >= from_timestamp) & (df['timestamp'] <= to_timestamp)]
            return df
        return pd.DataFrame(columns=['timestamp', 'price'])
    
    def fetch_dvol_data(
        self,
        asset: str,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch historical Deribit DVOL data from the competition infrastructure.
        
        DVOL is the 30-day implied volatility index from Deribit. This method allows
        models to access historical DVOL values for analysis or feature engineering.
        
        Args:
            asset: Asset symbol (must be "BTC")
            from_timestamp: Start time for historical data (optional)
            to_timestamp: End time for historical data (optional)
            
        Returns:
            DataFrame with columns: ['timestamp', 'dvol']
            DVOL values are in decimal format (0.40 = 40% annualized volatility)
            Empty DataFrame if no data available
            
        Note:
            In competition environment, DVOL data availability may be limited.
            For local testing, this returns cached data or empty DataFrame.
        """
        if asset in self._dvol_cache:
            df = self._dvol_cache[asset]
            if from_timestamp and to_timestamp:
                df = df[(df['timestamp'] >= from_timestamp) & (df['timestamp'] <= to_timestamp)]
            return df
        return pd.DataFrame(columns=['timestamp', 'dvol'])
    
    def tick(self, prices: Dict[str, List[Tuple[float, float]]]):
        """
        Receive price updates from the orchestrator.
        
        This method is called by the competition infrastructure to provide models
        with real-time price data. Models can store this data for use in predictions.
        
        The cache automatically limits itself to MAX_CACHE_ROWS most recent entries
        to prevent RAM exhaustion during long-running competitions.
        
        Args:
            prices: Dictionary mapping asset symbols to list of (timestamp, price) tuples
                    Example: {'BTC': [(1704067200.0, 42500.50), ...]}
        
        Note:
            Override this method if you need custom processing of incoming price data.
            The default implementation stores prices in internal cache with automatic
            size limiting (keeps most recent MAX_CACHE_ROWS entries).
        """
        for asset, price_list in prices.items():
            if price_list:
                df = pd.DataFrame(price_list, columns=['timestamp', 'price'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                
                if asset in self._price_cache:
                    # Concatenate new data
                    self._price_cache[asset] = pd.concat([self._price_cache[asset], df], ignore_index=True)
                    
                    # Limit cache size to prevent RAM issues
                    # Keep only the most recent MAX_CACHE_ROWS entries
                    if len(self._price_cache[asset]) > self.MAX_CACHE_ROWS:
                        self._price_cache[asset] = self._price_cache[asset].tail(self.MAX_CACHE_ROWS).reset_index(drop=True)
                else:
                    self._price_cache[asset] = df
