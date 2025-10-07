import json
import asyncio
from datetime import datetime
from typing import Dict, Any
from kafka import KafkaConsumer, KafkaProducer
from loguru import logger
from src.config.settings import settings
from src.models.model_handler import model_handler


class MLConsumer:
    """Kafka consumer that processes data and makes ML predictions."""
    
    def __init__(self):
        self.consumer = None
        self.producer = None
        self.setup_kafka()
    
    def setup_kafka(self):
        """Setup Kafka consumer and producer."""
        try:
            # Setup consumer
            self.consumer = KafkaConsumer(
                settings.kafka_input_topic,
                bootstrap_servers=settings.kafka_bootstrap_servers.split(','),
                group_id=settings.kafka_group_id,
                auto_offset_reset=settings.kafka_auto_offset_reset,
                enable_auto_commit=settings.kafka_enable_auto_commit,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None
            )
            
            # Setup producer for sending predictions
            self.producer = KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None
            )
            
            logger.info(f"Kafka consumer/producer setup complete")
            logger.info(f"Consuming from: {settings.kafka_input_topic}")
            logger.info(f"Publishing to: {settings.kafka_output_topic}")
            
        except Exception as e:
            logger.error(f"Failed to setup Kafka: {e}")
            raise
    
    def process_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single message and make ML prediction."""
        try:
            # Extract features from message
            features = message_data.get('features', [])
            message_id = message_data.get('id', 'unknown')
            
            if not features:
                raise ValueError("No features found in message")
            
            # Make prediction
            prediction_result = model_handler.predict([features])
            
            # Prepare result message
            result = {
                "input_id": message_id,
                "timestamp": datetime.now().isoformat(),
                "prediction": prediction_result['predictions'][0],
                "probability": prediction_result['probabilities'][0] if prediction_result['probabilities'] else None,
                "model_name": prediction_result['model_name'],
                "processing_info": {
                    "processed_at": datetime.now().isoformat(),
                    "consumer_group": settings.kafka_group_id,
                    "input_features_count": len(features)
                },
                "original_data": {
                    "timestamp": message_data.get('timestamp'),
                    "metadata": message_data.get('metadata', {})
                }
            }
            
            logger.info(f"Processed message {message_id}: prediction={result['prediction']}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "input_id": message_data.get('id', 'unknown'),
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "failed",
                "original_data": message_data
            }
    
    def send_prediction(self, prediction_data: Dict[str, Any]) -> bool:
        """Send prediction result to output topic."""
        try:
            future = self.producer.send(
                topic=settings.kafka_output_topic,
                key=prediction_data.get('input_id'),
                value=prediction_data
            )
            
            # Wait for confirmation
            record_metadata = future.get(timeout=10)
            
            logger.debug(f"Sent prediction to topic {record_metadata.topic}, "
                        f"partition {record_metadata.partition}, "
                        f"offset {record_metadata.offset}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send prediction: {e}")
            return False
    
    def consume_and_predict(self):
        """Main consumer loop."""
        logger.info("Starting ML consumer...")
        
        try:
            for message in self.consumer:
                try:
                    # Process the message
                    message_data = message.value
                    logger.debug(f"Received message: {message_data.get('id', 'unknown')}")
                    
                    # Make prediction
                    prediction_result = self.process_message(message_data)
                    
                    # Send prediction to output topic
                    success = self.send_prediction(prediction_result)
                    
                    if success:
                        logger.info(f"Successfully processed and sent prediction for message: "
                                  f"{message_data.get('id', 'unknown')}")
                    else:
                        logger.error(f"Failed to send prediction for message: "
                                   f"{message_data.get('id', 'unknown')}")
                        
                except Exception as e:
                    logger.error(f"Error processing Kafka message: {e}")
                    continue
                    
        except KeyboardInterrupt:
            logger.info("Stopping ML consumer...")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            self.close()
    
    def close(self):
        """Close Kafka connections."""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")
        
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")


def main():
    """Main function to run the ML consumer."""
    # Check model health before starting
    health = model_handler.health_check()
    if health['status'] != 'healthy':
        logger.error(f"Model health check failed: {health}")
        return
    
    logger.info("Model health check passed, starting consumer...")
    
    consumer = MLConsumer()
    try:
        consumer.consume_and_predict()
    except Exception as e:
        logger.error(f"Consumer error: {e}")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()