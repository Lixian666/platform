import threading

from base.c_resource import CResource


class CRedis(CResource):
    __instance_lock = threading.Lock()
    __redis_engines = list()

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(CRedis, "_instance"):
            with CRedis.__instance_lock:
                if not hasattr(CRedis, "_instance"):
                    CRedis._instance = object.__new__(cls)
                    CRedis._instance.reload_redis()
        return CRedis._instance

    def reload_redis(self):
        pass
