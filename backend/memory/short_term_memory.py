import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

RECENT_LIMIT = 5

def save_recent_to_redis(session_id, role, content):
    key = f"chat:{session_id}:recent"
    message = json.dumps({
        "role": role, 
        "content": content
    })
    
    redis_client.rpush(key, message)

    # keep last N message
    if redis_client.llen(key) > RECENT_LIMIT:
        redis_client.ltrim(key, -RECENT_LIMIT, -1)
    
def get_recent_from_redis(session_id):
    key = f"chat:{session_id}:recent"
    messages = redis_client.lrange(key, 0, -1)
    return [json.loads(msg) for msg in messages]