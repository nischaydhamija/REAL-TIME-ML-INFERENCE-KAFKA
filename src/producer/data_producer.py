import json
import time
import random
from datetime import datetime
from typing import Dict, Any
from kafka import KafkaProducer
from loguru import logger
from src.config.settings import settings


class DataProducer:
    """Kafka data producer for streaming sample data."""
    
    def __init__(self):
        self.producer = None
        self.connect_to_kafka()
    
    def connect_to_kafka(self):
        """Connect to Kafka broker."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8') if k else None
            )
            logger.info(f"Connected to Kafka at {settings.kafka_bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample data for ML inference."""
        return {
            "timestamp": datetime.now().isoformat(),
            "id": f"sample_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
            "features": [
                random.uniform(-2, 2) for _ in range(10)  # 10 random features
            ],
            "metadata": {
                "source": "data_producer",
                "version": "1.0",
                "batch_id": random.randint(1, 100)
            }
        }
    
    def send_data(self, data: Dict[str, Any], topic: str = None) -> bool:
        """Send data to Kafka topic."""
        topic = topic or settings.kafka_input_topic
        
        try:
            future = self.producer.send(
                topic=topic,
                key=data.get('id'),
                value=data
            )
            
            # Wait for the message to be sent
            record_metadata = future.get(timeout=10)
            
            logger.debug(f"Sent data to topic {record_metadata.topic}, "
                        f"partition {record_metadata.partition}, "
                        f"offset {record_metadata.offset}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send data to Kafka: {e}")
            return False
    
    def produce_continuous_data(self, interval: float = 1.0, max_messages: int = None):
        """Produce data continuously at specified intervals."""
        logger.info(f"Starting continuous data production (interval: {interval}s)")
        
        message_count = 0
        try:
            while True:
                if max_messages and message_count >= max_messages:
                    break
                
                data = self.generate_sample_data()
                success = self.send_data(data)
                
                if success:
                    message_count += 1
                    logger.info(f"Sent message {message_count}: {data['id']}")
                else:
                    logger.error(f"Failed to send message {message_count}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Stopping data production...")
        finally:
            self.close()
    
    def produce_batch_data(self, batch_size: int = 10):
        """Produce a batch of data."""
        logger.info(f"Producing batch of {batch_size} messages")
        
        successful_sends = 0
        for i in range(batch_size):
            data = self.generate_sample_data()
            if self.send_data(data):
                successful_sends += 1
                logger.info(f"Batch message {i+1}/{batch_size} sent: {data['id']}")
            else:
                logger.error(f"Failed to send batch message {i+1}/{batch_size}")
        
        logger.info(f"Batch complete: {successful_sends}/{batch_size} messages sent successfully")
        return successful_sends
    
    def close(self):
        """Close the Kafka producer."""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")


def main():
    """Main function to run the data producer."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kafka Data Producer")
    parser.add_argument("--mode", choices=["continuous", "batch"], default="batch",
                      help="Production mode")
    parser.add_argument("--interval", type=float, default=1.0,
                      help="Interval between messages in continuous mode (seconds)")
    parser.add_argument("--count", type=int, default=10,
                      help="Number of messages to send")
    
    args = parser.parse_args()
    
    producer = DataProducer()
    
    try:
        if args.mode == "continuous":
            producer.produce_continuous_data(
                interval=args.interval,
                max_messages=args.count if args.count > 0 else None
            )
        else:
            producer.produce_batch_data(batch_size=args.count)
    except Exception as e:
        logger.error(f"Producer error: {e}")
    finally:
        producer.close()


if __name__ == "__main__":
    main()