import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Kafka Configuration
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_input_topic: str = "input_data"
    kafka_output_topic: str = "predictions"
    kafka_group_id: str = "ml_inference_group"
    kafka_auto_offset_reset: str = "earliest"
    kafka_enable_auto_commit: bool = True
    
    # Model Configuration
    model_path: str = "models/trained_model.joblib"
    model_name: str = "sample_classifier"
    prediction_threshold: float = 0.5
    batch_size: int = 32
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = int(os.getenv("PORT", 8000))
    api_title: str = "Real-Time ML Inference API"
    api_version: str = "1.0.0"
    api_description: str = "FastAPI service for real-time machine learning predictions"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        protected_namespaces = ('settings_',)


# Global settings instance
settings = Settings()