# Real-Time Inference with Kafka

A real-time machine learning inference system using Apache Kafka for streaming data processing, FastAPI for serving predictions, and Docker for containerization.

## Architecture

This project implements a streaming ML inference pipeline with the following components:

- **Data Producer**: Generates/sends streaming data to Kafka topics
- **Kafka**: Message broker for data streaming
- **ML Inference Service**: FastAPI service that consumes from Kafka and serves predictions
- **Model**: Pre-trained ML model for making predictions
- **Docker**: Containerization for easy deployment

## Project Structure

```
.
├── src/
│   ├── producer/
│   │   └── data_producer.py      # Kafka data producer
│   ├── consumer/
│   │   └── ml_consumer.py        # ML inference consumer
│   ├── api/
│   │   └── inference_api.py      # FastAPI inference service
│   ├── models/
│   │   └── model_handler.py      # ML model loading and prediction
│   └── config/
│       └── settings.py           # Configuration settings
├── docker/
│   ├── docker-compose.yml        # Multi-service Docker setup
│   ├── Dockerfile.producer       # Producer service
│   ├── Dockerfile.consumer       # Consumer service
│   └── Dockerfile.api            # API service
├── data/
│   └── sample_data.json          # Sample data for testing
├── models/
│   └── trained_model.joblib      # Pre-trained model (placeholder)
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
└── README.md
```

## Prerequisites

- Docker and Docker Compose
- Python 3.8+

## Quick Start

1. **Clone and navigate to the project**:
   ```bash
   cd "REAL TIME INFERENCE with kafka"
   ```

2. **Start the services**:
   ```bash
   docker-compose -f docker/docker-compose.yml up --build
   ```

3. **Send test data** (in another terminal):
   ```bash
   python src/producer/data_producer.py
   ```

4. **Access the API**:
   - FastAPI docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## Services

### Data Producer
- Generates synthetic data and sends it to Kafka topics
- Configurable data generation patterns
- Supports batch and streaming modes

### ML Consumer
- Consumes data from Kafka topics
- Applies ML model for real-time predictions
- Publishes results to output topics

### Inference API
- FastAPI-based REST API for model predictions
- Real-time and batch prediction endpoints
- Model health monitoring

## Configuration

Environment variables in `.env`:
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker addresses
- `KAFKA_INPUT_TOPIC`: Input data topic
- `KAFKA_OUTPUT_TOPIC`: Predictions output topic
- `MODEL_PATH`: Path to the trained model
- `API_HOST`: FastAPI host
- `API_PORT`: FastAPI port

## Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run individual services**:
   ```bash
   # Start producer
   python src/producer/data_producer.py
   
   # Start consumer
   python src/consumer/ml_consumer.py
   
   # Start API
   python src/api/inference_api.py
   ```

## Model Training

The project includes a sample model. Replace `models/trained_model.joblib` with your own trained model.

## Monitoring

- Service health endpoints
- Kafka consumer lag monitoring
- Prediction latency metrics
- Model performance tracking

## License

MIT License