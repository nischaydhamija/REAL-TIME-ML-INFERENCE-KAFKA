#!/usr/bin/env python3
"""
Test script for the real-time inference project
"""

import sys
import os
import json
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models.model_handler import model_handler


def test_model():
    """Test the ML model"""
    print("🔬 Testing ML Model...")
    
    # Test model health
    health = model_handler.health_check()
    print(f"Model Health: {health['status']}")
    
    # Test single prediction
    test_features = [1.2, -0.5, 2.1, 0.8, -1.1, 0.3, 1.7, -0.9, 0.4, 1.5]
    result = model_handler.predict_single(test_features)
    
    print(f"Test Prediction:")
    print(f"- Input: {test_features}")
    print(f"- Prediction: {result['predictions'][0]}")
    print(f"- Probability: {result['probabilities'][0] if result['probabilities'] else 'N/A'}")
    print("✅ Model test passed!")
    return True


def test_data_generation():
    """Test data generation without Kafka"""
    print("\n📊 Testing Data Generation...")
    
    try:
        from src.producer.data_producer import DataProducer
        
        # Test data generation without Kafka connection
        producer = DataProducer.__new__(DataProducer)  # Create without __init__
        sample_data = producer.generate_sample_data()
        
        print(f"Generated sample data:")
        print(json.dumps(sample_data, indent=2))
        print("✅ Data generation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Data generation test failed: {e}")
        return False


def test_api_imports():
    """Test API imports"""
    print("\n🌐 Testing API Imports...")
    
    try:
        from src.api.inference_api import app
        from src.config.settings import settings
        
        print(f"API Configuration:")
        print(f"- Title: {settings.api_title}")
        print(f"- Version: {settings.api_version}")
        print(f"- Host: {settings.api_host}:{settings.api_port}")
        print("✅ API imports test passed!")
        return True
        
    except Exception as e:
        print(f"❌ API imports test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Real-Time Inference Project Test Suite")
    print("=" * 50)
    
    tests = [
        test_model,
        test_data_generation,
        test_api_imports
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! The project is ready for deployment.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())