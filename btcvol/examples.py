"""
Example models for the BTC DVOL Competition.
"""

import numpy as np
from .tracker import TrackerBase


class GARCHVolatilityModel(TrackerBase):
    """
    GARCH-inspired volatility model with mean reversion.
    
    This model predicts volatility using a mean reversion approach based on
    the prediction horizon. Volatility mean-reverts toward a base level,
    with the rate of reversion depending on the time horizon.
    """
    
    def __init__(self, base_vol: float = 0.42):
        """
        Initialize the GARCH volatility model.
        
        Args:
            base_vol: Long-term mean volatility level (default: 0.42 = 42%)
        """
        super().__init__()
        self.base_vol = base_vol
    
    def predict(self, asset: str, horizon: int, step: int) -> list:
        """
        Generate GARCH-style volatility predictions with mean reversion.
        
        The model adjusts predictions based on horizon:
        - Shorter horizons (1h): Higher volatility due to less mean reversion
        - Longer horizons (24h): Lower volatility due to more mean reversion
        """
        num_predictions = horizon // step
        
        # Calculate horizon-based adjustment factor
        # For 1h (3600s): factor = 1.0
        # For 24h (86400s): factor ≈ 0.20
        horizon_hours = horizon / 3600.0
        adjustment_factor = 1.0 / np.sqrt(horizon_hours / 24.0)
        
        # Generate predictions with slight random variation
        predictions = []
        for i in range(num_predictions):
            # Add small random noise to simulate market uncertainty
            noise = np.random.normal(0, 0.005)
            vol = self.base_vol * adjustment_factor + noise
            
            # Clip to reasonable range
            vol = np.clip(vol, 0.1, 1.0)
            predictions.append(vol)
        
        return predictions


class RandomWalkModel(TrackerBase):
    """
    Random walk model that generates predictions with small random variations.
    
    This model starts from a base volatility and adds small random increments,
    creating a random walk pattern.
    """
    
    def __init__(self, base_vol: float = 0.40, volatility: float = 0.02):
        """
        Initialize the random walk model.
        
        Args:
            base_vol: Starting volatility level (default: 0.40 = 40%)
            volatility: Standard deviation of random increments (default: 0.02)
        """
        super().__init__()
        self.base_vol = base_vol
        self.volatility = volatility
    
    def predict(self, asset: str, horizon: int, step: int) -> list:
        """Generate random walk volatility predictions."""
        num_predictions = horizon // step
        
        # Generate random walk
        increments = np.random.normal(0, self.volatility, num_predictions)
        walk = np.cumsum(increments)
        predictions = self.base_vol + walk
        
        # Clip to reasonable range [0.1, 1.0]
        predictions = np.clip(predictions, 0.1, 1.0)
        
        return predictions.tolist()


class LinearDecayModel(TrackerBase):
    """
    Model that predicts linearly decreasing volatility.
    
    This model assumes volatility will decrease linearly from a starting value
    to an ending value over the prediction horizon.
    """
    
    def __init__(self, start_vol: float = 0.45, end_vol: float = 0.35):
        """
        Initialize the linear decay model.
        
        Args:
            start_vol: Starting volatility (default: 0.45 = 45%)
            end_vol: Ending volatility (default: 0.35 = 35%)
        """
        super().__init__()
        self.start_vol = start_vol
        self.end_vol = end_vol
    
    def predict(self, asset: str, horizon: int, step: int) -> list:
        """Generate linearly decaying volatility predictions."""
        num_predictions = horizon // step
        predictions = np.linspace(self.start_vol, self.end_vol, num_predictions)
        return predictions.tolist()
