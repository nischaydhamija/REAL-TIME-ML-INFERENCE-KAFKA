from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
from loguru import logger
import uvicorn

from src.config.settings import settings
from src.models.model_handler import model_handler


# Pydantic models for request/response
class PredictionRequest(BaseModel):
    features: List[float]
    metadata: Optional[Dict[str, Any]] = None


class BatchPredictionRequest(BaseModel):
    data: List[PredictionRequest]


class PredictionResponse(BaseModel):
    prediction: int
    probability: Optional[List[float]] = None
    model_name: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class BatchPredictionResponse(BaseModel):
    predictions: List[PredictionResponse]
    total_samples: int
    processing_time: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    timestamp: str
    model_info: Dict[str, Any]


# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup."""
    logger.info("Starting ML Inference API...")
    
    # Check model health
    health = model_handler.health_check()
    if health['status'] != 'healthy':
        logger.error(f"Model health check failed: {health}")
    else:
        logger.info("Model health check passed")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    logger.info("Shutting down ML Inference API...")


@app.get("/")
async def root():
    """Serve the HTML landing page."""
    static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "index.html")
    if os.path.exists(static_path):
        return FileResponse(static_path)
    else:
        # Fallback to JSON response if HTML not found
        return {
            "project": "Real-Time ML Inference with Kafka",
            "description": "Production-ready system for serving ML predictions on streaming data",
            "version": settings.api_version,
            "author": "Nischay Dhamija",
            "github": "https://github.com/nischaydhamija/REAL-TIME-ML-INFERENCE-KAFKA",
            "tech_stack": ["Python", "FastAPI", "Apache Kafka", "Docker", "Scikit-learn"],
            "endpoints": {
                "health": "/health",
                "predict": "/predict",
                "batch_predict": "/predict/batch",
                "docs": "/docs",
                "model_info": "/model/info"
            },
            "status": "🚀 Running",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/info")
async def api_info():
    """API information endpoint (JSON)."""
    return {
        "project": "Real-Time ML Inference with Kafka",
        "description": "Production-ready system for serving ML predictions on streaming data",
        "version": settings.api_version,
        "author": "Nischay Dhamija",
        "github": "https://github.com/nischaydhamija/REAL-TIME-ML-INFERENCE-KAFKA",
        "tech_stack": ["Python", "FastAPI", "Apache Kafka", "Docker", "Scikit-learn"],
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "batch_predict": "/predict/batch",
            "docs": "/docs",
            "model_info": "/model/info"
        },
        "status": "🚀 Running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    health = model_handler.health_check()
    
    return HealthResponse(
        status=health['status'],
        model_loaded=health['model_loaded'],
        timestamp=datetime.now().isoformat(),
        model_info=health['model_info']
    )


@app.post("/predict", response_model=PredictionResponse)
async def predict_single(request: PredictionRequest):
    """Make a single prediction."""
    try:
        result = model_handler.predict_single(request.features)
        
        return PredictionResponse(
            prediction=result['predictions'][0],
            probability=result['probabilities'][0] if result['probabilities'] else None,
            model_name=result['model_name'],
            timestamp=datetime.now().isoformat(),
            metadata=request.metadata
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(request: BatchPredictionRequest):
    """Make batch predictions."""
    try:
        start_time = datetime.now()
        
        # Extract features from all requests
        features_list = [req.features for req in request.data]
        
        # Make batch predictions
        result = model_handler.predict(features_list)
        
        # Format responses
        predictions = []
        for i, req in enumerate(request.data):
            pred_response = PredictionResponse(
                prediction=result['predictions'][i],
                probability=result['probabilities'][i] if result['probabilities'] else None,
                model_name=result['model_name'],
                timestamp=datetime.now().isoformat(),
                metadata=req.metadata
            )
            predictions.append(pred_response)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return BatchPredictionResponse(
            predictions=predictions,
            total_samples=len(predictions),
            processing_time=f"{processing_time:.4f} seconds"
        )
    
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.get("/model/info")
async def get_model_info():
    """Get model information."""
    try:
        return model_handler.get_model_info()
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")


@app.post("/model/reload")
async def reload_model():
    """Reload the model from disk."""
    try:
        model_handler.load_model()
        return {
            "message": "Model reloaded successfully",
            "timestamp": datetime.now().isoformat(),
            "model_info": model_handler.get_model_info()
        }
    except Exception as e:
        logger.error(f"Error reloading model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reload model: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """Get API metrics."""
    # This is a placeholder for metrics collection
    # In a production environment, you would collect real metrics
    return {
        "api_version": settings.api_version,
        "model_name": settings.model_name,
        "timestamp": datetime.now().isoformat(),
        "uptime": "Available via monitoring tools",
        "requests_processed": "Available via monitoring tools",
        "average_latency": "Available via monitoring tools"
    }


def main():
    """Main function to run the FastAPI server."""
    logger.info(f"Starting FastAPI server on {settings.api_host}:{settings.api_port}")
    
    uvicorn.run(
        "src.api.inference_api:app",
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
        reload=False
    )


if __name__ == "__main__":
    main()