"""
Unit tests for btcvol package
"""

import pytest
import numpy as np
from btcvol import TrackerBase, test_model_locally
from btcvol.examples import GARCHVolatilityModel, RandomWalkModel, LinearDecayModel


class SimpleTestModel(TrackerBase):
    """Simple model for testing purposes."""
    
    def predict(self, asset: str, horizon: int, step: int):
        num_predictions = horizon // step
        return [0.40] * num_predictions


class TestTrackerBase:
    """Test TrackerBase functionality."""
    
    def test_abstract_predict_raises_error(self):
        """TrackerBase cannot be instantiated directly."""
        with pytest.raises(TypeError):
            TrackerBase()
    
    def test_simple_model_instantiation(self):
        """Simple model can be instantiated."""
        model = SimpleTestModel()
        assert model is not None
    
    def test_simple_model_prediction_1h(self):
        """Test 1-hour predictions."""
        model = SimpleTestModel()
        predictions = model.predict("BTC", 3600, 900)
        assert len(predictions) == 4
        assert all(p == 0.40 for p in predictions)
    
    def test_simple_model_prediction_24h(self):
        """Test 24-hour predictions."""
        model = SimpleTestModel()
        predictions = model.predict("BTC", 86400, 900)
        assert len(predictions) == 96
        assert all(p == 0.40 for p in predictions)


class TestExampleModels:
    """Test example models."""
    
    def test_garch_model(self):
        """Test GARCH volatility model."""
        model = GARCHVolatilityModel(base_vol=0.42)
        predictions = model.predict("BTC", 3600, 900)
        
        assert len(predictions) == 4
        assert all(isinstance(p, float) for p in predictions)
        assert all(0.1 <= p <= 1.0 for p in predictions)
    
    def test_random_walk_model(self):
        """Test random walk model."""
        model = RandomWalkModel(base_vol=0.40, volatility=0.02)
        predictions = model.predict("BTC", 3600, 900)
        
        assert len(predictions) == 4
        assert all(isinstance(p, float) for p in predictions)
        assert all(0.1 <= p <= 1.0 for p in predictions)
    
    def test_linear_decay_model(self):
        """Test linear decay model."""
        model = LinearDecayModel(start_vol=0.45, end_vol=0.35)
        predictions = model.predict("BTC", 3600, 900)
        
        assert len(predictions) == 4
        assert all(isinstance(p, float) for p in predictions)
        assert predictions[0] >= predictions[-1]  # Decreasing
        assert np.isclose(predictions[0], 0.45, atol=0.01)
        assert np.isclose(predictions[-1], 0.35, atol=0.01)


class TestLocalTesting:
    """Test local testing utilities."""
    
    def test_test_model_locally_passes(self):
        """test_model_locally should pass for valid model."""
        result = test_model_locally(SimpleTestModel, verbose=False)
        assert result is True
    
    def test_test_model_locally_with_garch(self):
        """test_model_locally should pass for GARCH model."""
        result = test_model_locally(GARCHVolatilityModel, verbose=False)
        assert result is True


class TestPredictionFormats:
    """Test prediction format requirements."""
    
    def test_prediction_count_1h(self):
        """1-hour horizon should return 4 predictions."""
        model = SimpleTestModel()
        predictions = model.predict("BTC", 3600, 900)
        assert len(predictions) == 4
    
    def test_prediction_count_24h(self):
        """24-hour horizon should return 96 predictions."""
        model = SimpleTestModel()
        predictions = model.predict("BTC", 86400, 900)
        assert len(predictions) == 96
    
    def test_predictions_are_numeric(self):
        """All predictions should be numeric."""
        model = GARCHVolatilityModel()
        predictions = model.predict("BTC", 3600, 900)
        assert all(isinstance(p, (int, float)) for p in predictions)
    
    def test_predictions_in_range(self):
        """Predictions should be in reasonable range."""
        model = GARCHVolatilityModel()
        predictions = model.predict("BTC", 3600, 900)
        assert all(0 <= p <= 1.5 for p in predictions)  # Allow some flexibility


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
