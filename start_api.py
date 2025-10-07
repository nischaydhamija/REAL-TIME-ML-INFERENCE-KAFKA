#!/usr/bin/env python3
"""
Standalone API server for real-time ML inference
This version runs without Kafka dependencies for development and testing
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.api.inference_api import main

if __name__ == "__main__":
    print("🚀 Starting Real-Time ML Inference API...")
    print("📝 API Documentation will be available at: http://localhost:8000/docs")
    print("🏥 Health check available at: http://localhost:8000/health")
    print("🔄 Single predictions at: http://localhost:8000/predict")
    print("📦 Batch predictions at: http://localhost:8000/predict/batch")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 60)
    
    main()