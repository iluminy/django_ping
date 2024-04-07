import redis
from django.conf import settings


class ConnectedUsers:
    KEY_CONNECTED_USERS = 'connected_users'

    redis_sync = None
    redis_async = None

    def __init__(self, sync_mode: bool = False, async_mode: bool = False):
        if not (sync_mode ^ async_mode):
            raise ValueError('You must set one of the connection modes.')
        connection_params = {
            'host': settings.REDIS_HOST,
            'port': settings.REDIS_PORT,
            'db': settings.REDIS_DATA_DB,
            'decode_responses': True,
        }
        if sync_mode:
            self.redis_sync = redis.Redis(**connection_params)
        if async_mode:
            self.redis_async = redis.asyncio.Redis(**connection_params)

    def __enter__(self):
        return self

    async def __aenter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self.aclose()

    async def aadd(self, username: str, task_id: str):
        await self.redis_async.sadd(self.KEY_CONNECTED_USERS, username)
        await self.redis_async.sadd(task_id.replace('.', '_'), username)

    async def aremove(self, username: str, task_id: str):
        await self.redis_async.srem(self.KEY_CONNECTED_USERS, username)
        await self.redis_async.srem(task_id.replace('.', '_'), username)

    def get(self):
        """
        Returns usernames of connected users (listeners).
        """
        return self.redis_sync.smembers(self.KEY_CONNECTED_USERS)

    def get_for_process(self, task_id: str):
        """
        Returns usernames of listeners for a single process.
        """
        return self.redis_sync.smembers(task_id.replace('.', '_'))

    def flush_users(self):
        self.redis_sync.delete(self.KEY_CONNECTED_USERS)

    def close(self):
        self.redis_sync.close()

    async def aclose(self):
        await self.redis_async.aclose()
