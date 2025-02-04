import pika
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def upload(file, fs, channel, access):
    try:
        fid = fs.put(file)
        logger.info(f"File uploaded successfully with file ID: {fid}")
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return "Internal server error", 500

    message = {
        "video_id": str(fid),
        "mp3_id": None,
        "username": access["username"],
    }
    logger.debug(f"Message to be sent: {message}")
    
    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        logger.info(f"Message successfully sent to RabbitMQ with video_id: {message['video_id']}")
    except Exception as err:
        logger.error(f"Exception occurred while publishing message: {err}")
        fs.delete(fid)
        return "Internal server error", 500

    return None, 200
