import pika, json

def upload(file, fs, channel, access):
    try:
        fid = fs.put(file)
    except Exception as e:
        return "Internal server error" ,  500
    
    message = {
        "video_id": str(fid),
        "mp3_id": None,
        "userName": access["userName"],
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            property=pika.BasicProperties(
                delivery_method=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except:
        fs.delete(fid)
        return "Internal server error", 500

