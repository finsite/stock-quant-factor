"""Handles message queue consumption for RabbitMQ and SQS.

This module receives instrument data, applies factor-based analysis,
and sends resulting signals to the output handler.
"""

import json
import time

import boto3
import pika
from botocore.exceptions import BotoCoreError, NoCredentialsError

from app import config
from app.factor_engine import run_factor_analysis
from app.logger import setup_logger
from app.output_handler import send_to_output

logger = setup_logger(__name__)

# Initialize SQS client if needed
sqs_client = None
if config.get_queue_type() == "sqs":
    try:
        sqs_client = boto3.client("sqs", region_name=config.get_sqs_region())
        logger.info(f"SQS client initialized for region {config.get_sqs_region()}")
    except (BotoCoreError, NoCredentialsError) as e:
        logger.error("Failed to initialize SQS client: %s", e)
        sqs_client = None


def connect_to_rabbitmq() -> pika.BlockingConnection:
    """Connects to RabbitMQ with retry logic."""
    retries = 5
    while retries > 0:
        try:
            credentials = pika.PlainCredentials(
                username=config.get_rabbitmq_user(),
                password=config.get_rabbitmq_password(),
            )
            conn = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=config.get_rabbitmq_host(),
                    port=config.get_rabbitmq_port(),
                    virtual_host=config.get_rabbitmq_vhost(),
                    credentials=credentials,
                )
            )
            if conn.is_open:
                logger.info("Connected to RabbitMQ")
                return conn
        except Exception as e:
            retries -= 1
            logger.warning("RabbitMQ connection failed: %s. Retrying in 5s...", e)
            time.sleep(5)
    raise ConnectionError("Could not connect to RabbitMQ after retries")


def consume_rabbitmq() -> None:
    """Consumes messages from RabbitMQ."""
    connection = connect_to_rabbitmq()
    channel = connection.channel()

    channel.exchange_declare(
        exchange=config.get_rabbitmq_exchange(), exchange_type="topic", durable=True
    )
    channel.queue_declare(queue=config.get_rabbitmq_queue(), durable=True)
    channel.queue_bind(
        exchange=config.get_rabbitmq_exchange(),
        queue=config.get_rabbitmq_queue(),
        routing_key=config.get_rabbitmq_routing_key(),
    )

    def callback(ch, method, properties, body: bytes) -> None:
        """

        :param ch: param method:
        :param properties: param body: bytes:
        :param method: param body: bytes:
        :param body: bytes:
        :param body: 
        :type body: bytes :
        :param body: 
        :type body: bytes :
        :param body: bytes: 

        
        """
        try:
            message = json.loads(body)
            logger.info("📩 Received message: %s", message)

            result = run_factor_analysis(message)
            if result:
                result["source"] = "FactorModel"
                send_to_output(result)

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except json.JSONDecodeError:
            logger.error("❌ Invalid JSON: %s", body)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error("❌ Error processing message: %s", e)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue=config.get_rabbitmq_queue(), on_message_callback=callback)
    logger.info("📡 Waiting for messages from RabbitMQ...")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Gracefully stopping RabbitMQ consumer...")
        channel.stop_consuming()
    finally:
        connection.close()
        logger.info("RabbitMQ connection closed.")


def consume_sqs() -> None:
    """Consumes messages from Amazon SQS."""
    if not sqs_client or not config.get_sqs_queue_url():
        logger.error("SQS not initialized or missing queue URL.")
        return

    logger.info("📡 Polling for SQS messages...")

    while True:
        try:
            response = sqs_client.receive_message(
                QueueUrl=config.get_sqs_queue_url(),
                MaxNumberOfMessages=config.get_batch_size(),
                WaitTimeSeconds=10,
            )

            for msg in response.get("Messages", []):
                try:
                    body = json.loads(msg["Body"])
                    logger.info("📩 Received SQS message: %s", body)

                    result = run_factor_analysis(body)
                    if result:
                        result["source"] = "FactorModel"
                        send_to_output(result)

                    sqs_client.delete_message(
                        QueueUrl=config.get_sqs_queue_url(), ReceiptHandle=msg["ReceiptHandle"]
                    )
                    logger.info("✅ Deleted SQS message: %s", msg["MessageId"])
                except Exception as e:
                    logger.error("❌ Error processing SQS message: %s", e)
        except Exception as e:
            logger.error("SQS polling failed: %s", e)
            time.sleep(config.get_polling_interval())


def consume_messages() -> None:
    """Starts the appropriate consumer based on QUEUE_TYPE."""
    if config.get_queue_type() == "rabbitmq":
        consume_rabbitmq()
    elif config.get_queue_type() == "sqs":
        consume_sqs()
    else:
        logger.error("Invalid QUEUE_TYPE specified. Use 'rabbitmq' or 'sqs'.")
