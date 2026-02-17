"""
Base class for BTC DVOL prediction models.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Tuple
import pandas as pd
from datetime import datetime, timedelta, timezone
import requests


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
    
    # API endpoints
    CRUNCH_API_URL = "https://pricedb.crunchdao.com/v1/prices"
    DERIBIT_API_URL = "https://www.deribit.com/api/v2/public/get_volatility_index_data"
    
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
        Fetch historical price data from cache or CrunchDAO API.
        
        This method tries cache first (populated by tick() in production),
        then falls back to API if cache is empty or insufficient.
        
        Args:
            asset: Asset symbol (e.g., "BTC")
            from_timestamp: Start time for historical data (optional)
            to_timestamp: End time for historical data (optional)
            
        Returns:
            DataFrame with columns: ['timestamp', 'price']
            Empty DataFrame if no data available
        """
        # Try cache first
        if asset in self._price_cache and len(self._price_cache[asset]) > 50:
            df = self._price_cache[asset].copy()
            if from_timestamp and to_timestamp:
                df = df[(df['timestamp'] >= from_timestamp) & (df['timestamp'] <= to_timestamp)]
            return df
        
        # Fallback: fetch from CrunchDAO API
        try:
            now = datetime.now(timezone.utc)
            from_dt = from_timestamp if from_timestamp else now - timedelta(days=30)
            to_dt = to_timestamp if to_timestamp else now
            
            params = {
                "asset": asset,
                "from": from_dt.isoformat(),
                "to": to_dt.isoformat()
            }
            
            response = requests.get(self.CRUNCH_API_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get("close") and data.get("timestamp"):
                df = pd.DataFrame({
                    "timestamp": pd.to_datetime(data["timestamp"], unit="s"),
                    "price": data["close"]
                })
                return df.sort_values("timestamp").reset_index(drop=True)
        except Exception as e:
            print(f"⚠ Error fetching price data from API: {e}")
        
        return pd.DataFrame(columns=['timestamp', 'price'])
    
    def fetch_dvol_data(
        self,
        asset: str,
        from_timestamp: Optional[datetime] = None,
        to_timestamp: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Fetch historical Deribit DVOL data from cache or Deribit API.
        
        DVOL is the 30-day implied volatility index from Deribit. This method tries
        cache first (populated by tick() in production), then falls back to API.
        
        Args:
            asset: Asset symbol (must be "BTC")
            from_timestamp: Start time for historical data (optional)
            to_timestamp: End time for historical data (optional)
            
        Returns:
            DataFrame with columns: ['timestamp', 'dvol']
            DVOL values are in decimal format (0.40 = 40% annualized volatility)
            Empty DataFrame if no data available
        """
        # Try cache first
        if asset in self._dvol_cache and len(self._dvol_cache[asset]) > 50:
            df = self._dvol_cache[asset].copy()
            if from_timestamp and to_timestamp:
                df = df[(df['timestamp'] >= from_timestamp) & (df['timestamp'] <= to_timestamp)]
            return df
        
        # Fallback: fetch from Deribit API (only fetches historical data, not future)
        try:
            now = datetime.now(timezone.utc)
            # Fetch last 7 days of historical data (Deribit only provides past data)
            start_dt = from_timestamp if from_timestamp else now - timedelta(days=7)
            end_dt = to_timestamp if to_timestamp else now
            
            # Ensure we're not requesting future data
            if end_dt > now:
                end_dt = now
            if start_dt > now:
                start_dt = now - timedelta(days=7)
            
            # Convert to seconds (Deribit uses seconds, not milliseconds for some endpoints)
            start_ts = int(start_dt.timestamp())
            end_ts = int(end_dt.timestamp())
            
            params = {
                "currency": asset,
                "start_timestamp": start_ts,
                "end_timestamp": end_ts
            }
            
            response = requests.get(self.DERIBIT_API_URL, params=params, timeout=15)
            response.raise_for_status()
            payload = response.json()
            
            # Parse different response formats
            if "result" in payload:
                data = payload["result"]
                if isinstance(data, dict) and "data" in data:
                    data = data["data"]
            else:
                data = payload
            
            rows = []
            for item in data:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    ts, val = item[0], item[1]
                elif isinstance(item, dict):
                    ts = item.get("timestamp") or item.get("t")
                    val = item.get("volatility") or item.get("v") or item.get("value")
                else:
                    continue
                
                if ts is None or val is None:
                    continue
                
                # Try both milliseconds and seconds for timestamp
                try:
                    timestamp = pd.to_datetime(ts, unit="ms")
                except:
                    timestamp = pd.to_datetime(ts, unit="s")
                
                rows.append({
                    "timestamp": timestamp,
                    "dvol": float(val)
                })
            
            if rows:
                df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
                return df
        except Exception as e:
            # Silently fail in production, only print in debug mode
            pass
        
        return pd.DataFrame(columns=['timestamp', 'dvol'])
    
    def fetch_latest_dvol_data(self, step: int = 900) -> pd.DataFrame:
        """
        Helper method to fetch recent DVOL data at specified resolution.
        
        Args:
            step: Time resolution in seconds (default: 900 = 15 minutes)
            
        Returns:
            DataFrame with timestamp and dvol columns
        """
        return self.fetch_dvol_data("BTC")
    
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
