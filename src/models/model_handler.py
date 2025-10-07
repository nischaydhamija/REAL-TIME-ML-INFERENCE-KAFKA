import os
import joblib
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Union
from loguru import logger
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from src.config.settings import settings


class ModelHandler:
    """Handle ML model loading, prediction, and management."""
    
    def __init__(self, model_path: str = None):
        self.model_path = model_path or settings.model_path
        self.model = None
        self.model_metadata = {}
        self.load_model()
    
    def load_model(self) -> None:
        """Load the ML model from disk or create a sample model."""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.model_metadata = {
                    "model_type": type(self.model).__name__,
                    "features": getattr(self.model, 'n_features_in_', 'unknown'),
                    "status": "loaded_from_disk"
                }
                logger.info(f"Model loaded from {self.model_path}")
            else:
                self._create_sample_model()
                logger.warning(f"Model not found at {self.model_path}, created sample model")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self._create_sample_model()
    
    def _create_sample_model(self) -> None:
        """Create and train a sample model for demonstration."""
        # Generate sample data
        X, y = make_classification(
            n_samples=1000,
            n_features=10,
            n_informative=5,
            n_redundant=2,
            n_classes=2,
            random_state=42
        )
        
        # Train a simple model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        
        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        
        self.model_metadata = {
            "model_type": "RandomForestClassifier",
            "features": 10,
            "status": "sample_model_created"
        }
        
        logger.info(f"Sample model created and saved to {self.model_path}")
    
    def predict(self, data: Union[List, np.ndarray, pd.DataFrame]) -> Dict[str, Any]:
        """Make predictions on input data."""
        try:
            # Convert input to numpy array
            if isinstance(data, list):
                data = np.array(data)
            elif isinstance(data, pd.DataFrame):
                data = data.values
            
            # Ensure data is 2D
            if data.ndim == 1:
                data = data.reshape(1, -1)
            
            # Make predictions
            predictions = self.model.predict(data)
            probabilities = None
            
            # Get probabilities if available
            if hasattr(self.model, 'predict_proba'):
                probabilities = self.model.predict_proba(data)
            
            return {
                "predictions": predictions.tolist(),
                "probabilities": probabilities.tolist() if probabilities is not None else None,
                "model_name": settings.model_name,
                "num_samples": len(predictions)
            }
        
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise ValueError(f"Prediction failed: {str(e)}")
    
    def predict_single(self, features: List[float]) -> Dict[str, Any]:
        """Make prediction on a single sample."""
        return self.predict([features])
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and metadata."""
        return {
            "model_name": settings.model_name,
            "model_path": self.model_path,
            "model_loaded": self.model is not None,
            "metadata": self.model_metadata
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform model health check."""
        try:
            # Test prediction with dummy data
            dummy_data = np.random.rand(1, self.model_metadata.get('features', 10))
            result = self.predict(dummy_data)
            
            return {
                "status": "healthy",
                "model_loaded": True,
                "test_prediction_successful": True,
                "model_info": self.get_model_info()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "model_loaded": self.model is not None,
                "test_prediction_successful": False,
                "error": str(e),
                "model_info": self.get_model_info()
            }


# Global model handler instance
model_handler = ModelHandler()