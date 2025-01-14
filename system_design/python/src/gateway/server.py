import os, gridfs, pika , json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_SVC import access
from storage import util


server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))

channel = connection.channel()

@server.route("/login", methods=["POST"])
def login():
   tokens, err = access.login(request)

   if not err:
      return tokens
   else:
      return err
   
@server.route("/upload", methods=["POST"])
def upload():
   token, err = validate.token(request)

   token = json.loads(token)

   if token["admin"]:
      if len(request.files) > 1 or len(request.files) < 1:
         return "exactly one file required", 400
      
      for _, file in request.files.items():
         err = util.upload(file, fs, channel, token)

         if err:
            return err, 400
         
      return "success", 200
   else:
      return "not authorized", 401

@server.route("/download", methods=["GET"])
def download():
   pass

if __name__ == "__main__":
   server.run(host="0.0.0.0", port=8080)
         
