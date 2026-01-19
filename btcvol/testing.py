"""
Local testing utilities for BTC DVOL models.
"""

from typing import Type, List
from .tracker import TrackerBase


def test_model_locally(model_class: Type[TrackerBase], verbose: bool = True) -> bool:
    """
    Test a model locally to ensure it implements the required interface.
    
    This function validates that your model:
    - Properly inherits from TrackerBase
    - Implements the predict() method correctly
    - Returns predictions in the correct format
    
    Args:
        model_class: Your model class (not an instance)
        verbose: Print detailed test results
        
    Returns:
        True if all tests pass, False otherwise
        
    Example:
        >>> from btcvol import TrackerBase, test_model_locally
        >>> class MyModel(TrackerBase):
        ...     def predict(self, asset, horizon, step):
        ...         return [0.40] * (horizon // step)
        >>> test_model_locally(MyModel)
        ✓ Model instantiation: PASSED
        ✓ Predict method exists: PASSED
        ✓ 1-hour predictions (4 values): PASSED
        ✓ 24-hour predictions (96 values): PASSED
        All tests passed!
        True
    """
    print("\n" + "="*60)
    print("BTC DVOL Model Local Testing")
    print("="*60 + "\n")
    
    try:
        # Test 1: Instantiation
        model = model_class()
        if verbose:
            print("✓ Model instantiation: PASSED")
        
        # Test 2: Check predict method exists
        if not hasattr(model, 'predict'):
            print("✗ Model must implement predict() method: FAILED")
            return False
        if verbose:
            print("✓ Predict method exists: PASSED")
        
        # Test 3: Test 1-hour horizon predictions
        try:
            predictions_1h = model.predict("BTC", 3600, 900)
            if not isinstance(predictions_1h, list):
                print(f"✗ predict() must return a list, got {type(predictions_1h)}: FAILED")
                return False
            if len(predictions_1h) != 4:
                print(f"✗ 1-hour horizon should return 4 predictions, got {len(predictions_1h)}: FAILED")
                return False
            if not all(isinstance(p, (int, float)) for p in predictions_1h):
                print("✗ All predictions must be numeric values: FAILED")
                return False
            if verbose:
                print(f"✓ 1-hour predictions (4 values): PASSED")
                print(f"  Sample predictions: {predictions_1h}")
        except Exception as e:
            print(f"✗ Error generating 1-hour predictions: {e}")
            return False
        
        # Test 4: Test 24-hour horizon predictions
        try:
            predictions_24h = model.predict("BTC", 86400, 900)
            if len(predictions_24h) != 96:
                print(f"✗ 24-hour horizon should return 96 predictions, got {len(predictions_24h)}: FAILED")
                return False
            if verbose:
                print(f"✓ 24-hour predictions (96 values): PASSED")
                print(f"  Sample predictions: {predictions_24h[:5]}...")
        except Exception as e:
            print(f"✗ Error generating 24-hour predictions: {e}")
            return False
        
        # Test 5: Check prediction values are reasonable
        all_predictions = predictions_1h + predictions_24h
        if any(p < 0 or p > 1 for p in all_predictions):
            print("⚠ Warning: Some predictions outside 0-1 range (should be decimal, e.g., 0.40 = 40%)")
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60 + "\n")
        print("Your model is ready for submission to the competition.")
        print("Next steps:")
        print("  1. Review your predictions to ensure they make sense")
        print("  2. Test with historical data if available")
        print("  3. Submit to the competition platform")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


def validate_predictions(predictions: List[float], horizon: int, step: int) -> bool:
    """
    Validate that predictions meet competition requirements.
    
    Args:
        predictions: List of predicted volatility values
        horizon: Expected time horizon in seconds
        step: Prediction resolution in seconds
        
    Returns:
        True if predictions are valid, False otherwise
    """
    expected_count = horizon // step
    
    if not isinstance(predictions, list):
        print(f"Predictions must be a list, got {type(predictions)}")
        return False
    
    if len(predictions) != expected_count:
        print(f"Expected {expected_count} predictions for horizon={horizon}s, step={step}s")
        print(f"Got {len(predictions)} predictions")
        return False
    
    if not all(isinstance(p, (int, float)) for p in predictions):
        print("All predictions must be numeric values")
        return False
    
    return True
