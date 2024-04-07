from contextlib import contextmanager
import time

from django.conf import settings
from redis import Redis
from main.tasks import ping_task


class ProcessManager:
    KEY_PENDING_PROCESSES = 'pending_processes'
    KEY_RUNNING_PROCESSES = 'running_processes'
    KEY_TO_TERMINATE = 'processes_to_terminate'

    def __init__(self):
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DATA_DB,
            decode_responses=True
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    @contextmanager
    def _simple_lock(self, ip: str):
        """
        This is a simple lock to ensure that only one instance starting
        process. It's inspired by this article:
        https://docs.celeryq.dev/en/latest/tutorials/task-cookbook.html#ensuring-a-task-is-only-executed-one-at-a-time
        """
        LOCK_EXPIRE = 20  # Lock expires in 20 seconds.
        status = self.redis.set(ip, 'lock', LOCK_EXPIRE, nx=True)
        timeout_at = time.monotonic() + LOCK_EXPIRE
        try:
            yield status
        finally:
            if time.monotonic() < timeout_at and status:
                # Don't release the lock if we exceeded the timeout
                # to lessen the chance of releasing an expired lock
                # owned by someone else
                # also don't release the lock if we didn't acquire it
                self.redis.delete(ip)

    def start(self, ip: str):
        with self._simple_lock(ip) as acquired:
            if not acquired or ip in self.get_pending() or ip in self.get_running():
                raise ProcessAlreadyStarted
            self.redis.sadd(self.KEY_PENDING_PROCESSES, ip)
            ping_task.delay(ip)

    def stop(self, ip: str):
        self.redis.sadd(self.KEY_TO_TERMINATE, ip)

    def clean_up_process(self, ip: str):
        self.redis.srem(self.KEY_TO_TERMINATE, ip)
        self.redis.srem(self.KEY_PENDING_PROCESSES, ip)
        self.redis.srem(self.KEY_RUNNING_PROCESSES, ip)

    def mark_as_running(self, ip: str):
        self.redis.sadd(self.KEY_RUNNING_PROCESSES, ip)
        self.redis.srem(self.KEY_PENDING_PROCESSES, ip)

    def get_pending(self):
        return self.redis.smembers(self.KEY_PENDING_PROCESSES)

    def get_running(self):
        return self.redis.smembers(self.KEY_RUNNING_PROCESSES)

    def get_terminating(self):
        return self.redis.smembers(self.KEY_TO_TERMINATE)

    def flush_processes(self):
        self.redis.delete(self.KEY_TO_TERMINATE)
        self.redis.delete(self.KEY_RUNNING_PROCESSES)
        self.redis.delete(self.KEY_PENDING_PROCESSES)

    def close(self):
        self.redis.close()


class ProcessAlreadyStarted(Exception):
    pass
