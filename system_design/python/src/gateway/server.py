import os
import gridfs
import pika
import json
import logging
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_SVC import access
from storage import util

# Initialize Flask app
server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://192.168.49.2:27017/videos"

# Set up MongoDB and GridFS
mongo = PyMongo(server)
fs = gridfs.GridFS(mongo.db)

# Set up RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@server.route("/login", methods=["POST"])
def login():
    tokens, err = access.login(request)
    if not err:
        logger.info("Login successful.")
        return tokens
    else:
        logger.error(f"Login error: {err}")
        return err

@server.route("/upload", methods=["POST"])
def upload():
    try:
        token, err = validate.token(request)
        logger.debug(f"Token validation response - Token: {token}, Error: {err}")

        if err:
            logger.warning(f"Token validation failed: {err}")
            return {"error": err[0]}, err[1]

        token = json.loads(token)
        logger.debug(f"Parsed token: {token}")

        if token.get("admin"):
            if len(request.files) != 1:
                logger.warning("Upload request contains an incorrect number of files.")
                return "exactly one file required", 400

            for _, file in request.files.items():
                err, status = util.upload(file, fs, channel, token)
                if err:
                    logger.error(f"File upload failed: {err}, Status: {status}")
                    return {"error": err}, status

            logger.info("File uploaded successfully.")
            return {"status": "success"}, 200
        else:
            logger.warning("Unauthorized upload attempt.")
            return {"error": "not authorized"}, 401
    except Exception as e:
        logger.exception("An error occurred during the upload process.")
        return {"error": "Internal server error"}, 500

@server.route("/download", methods=["GET"])
def download():
    pass  # Placeholder for future functionality

@server.route("/test_mongo", methods=["GET"])
def test_mongo():
    try:
        # Attempting to fetch data from the MongoDB 'videos' collection to ensure connectivity
        test_data = mongo.db.videos.find_one()
        if test_data:
            return {"status": "MongoDB connection successful", "data": test_data}, 200
        else:
            return {"error": "No data found"}, 404
    except Exception as e:
        logger.exception("Failed to connect to MongoDB")
        return {"error": "MongoDB connection failed"}, 500

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
