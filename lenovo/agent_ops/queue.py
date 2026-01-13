from rq import Queue
from redis import Redis
from agent_ops.config import get_settings

_settings = get_settings()

redis_conn = Redis.from_url(_settings.redis_url)
queue = Queue(_settings.rq_queue, connection=redis_conn)
