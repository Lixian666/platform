from base.c_exceptions import DBLinkException

try:
    import redis
except Exception:
    pass
from base.c_resource import CResource
from base.c_utils import CUtils


class CRedisEngine(CResource):
    Name_Db = 'db'
    Name_Decode_Responses = 'decode_responses'

    # 即redis池
    __engine = None

    def __init__(self, redis_option):
        self.__redis_option = redis_option

        self._redis_conn_id = CUtils.dict_value_by_name(redis_option, self.Name_ID, self.DB_Server_ID_Default)
        self._redis_conn_host = CUtils.dict_value_by_name(redis_option, CResource.Name_Host, self.Host_LocalHost)
        self._redis_conn_port = CUtils.dict_value_by_name(redis_option, CResource.Name_Port, '6379')
        self._redis_conn_password_native = CUtils.dict_value_by_name(redis_option, CResource.Name_Password, '')
        self._redis_conn_password = self._redis_conn_password_native

        self._redis_conn_db = CUtils.dict_value_by_name(redis_option, self.Name_Db, 0)
        self._redis_conn_decode_responses = CUtils.dict_value_by_name(redis_option, self.Name_Decode_Responses, True)

    @property
    def redis_conn_id(self):
        """
        返回redis连接id
        Returns:
            str: 返回redis连接id

        """
        return self._redis_conn_id

    @property
    def redis_option(self):
        """
            获取数据库配置信息中的可选项
        Returns:
            数据库可选项信息
        """
        return self.__redis_option

    def create_engine(self):
        """
        创建引擎
        Returns:
            返回一个引擎对象创建语句

        """
        redis_pool = redis.ConnectionPool(
            host=self._redis_conn_host, port=self._redis_conn_port, password=self._redis_conn_password,
            db=self._redis_conn_db, decode_responses=self._redis_conn_decode_responses
        )
        return redis_pool

    def engine(self):
        """
        返回一个引擎
        Returns:
            返回一个引擎对象

        """
        # noinspection PyBroadException
        try:
            if self.__engine is None:
                self.__engine = self.create_engine()

            return self.__engine
        except Exception:
            raise DBLinkException(self._redis_conn_id)

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        """
        在 Redis 中设置值，默认，不存在则创建，存在则修改(值)。

        Args:
            name: 键
            value: 值
            ex: 过期时间（秒）
            px: 过期时间（毫秒）
            nx: 如果设置为True，则只有name不存在时，当前set操作才执行
            xx: 如果设置为True，则只有name存在时，当前set操作才执行

        Returns:
            无返回

        """
        redis_obj = None
        # noinspection PyBroadException
        try:
            redis_obj = redis.Redis(connection_pool=self.engine())
            name = CUtils.any_2_str(name)
            value = CUtils.any_2_str(value)
            redis_obj.set(name, value, ex, px, nx, xx)
        except Exception as error:
            Exception('在 Redis 中设置值时发生问题，详细原因为: {0}'.format(str(error)))
        finally:
            if redis_obj is not None:
                redis_obj.close()

    def set_batch(self, name_value_tuple_list, ex=None, px=None, nx=False, xx=False):
        """
        在 Redis 中设置值，默认，不存在则创建，存在则修改(键值元组)。

        Args:
            name_value_tuple_list: 键值元组列表 [(name1,value1),(name2,value2)]
            ex: 过期时间（秒）
            px: 过期时间（毫秒）
            nx: 如果设置为True，则只有name不存在时，当前set操作才执行
            xx: 如果设置为True，则只有name存在时，当前set操作才执行

        Returns:
            无返回

        """
        redis_obj = None
        redis_pipeline = None
        # noinspection PyBroadException
        try:
            redis_obj = redis.Redis(connection_pool=self.engine())
            redis_pipeline = redis_obj.pipeline()

            for this_tuple_one in name_value_tuple_list:
                this_name = CUtils.any_2_str(this_tuple_one[0])
                this_value = CUtils.any_2_str(this_tuple_one[1])
                redis_pipeline.set(this_name, this_value, ex, px, nx, xx)

            redis_pipeline.execute()

        except Exception as error:
            Exception('在 Redis 中设置值时发生问题，详细原因为: {0}'.format(str(error)))
        finally:
            if redis_pipeline is not None:
                redis_pipeline.close()

            if redis_obj is not None:
                redis_obj.close()

    def get(self, name):
        """
        返回键name处的值，如果键不存在则返回None

        Args:
            name: 键

        Returns:
            值

        """
        redis_obj = None
        # noinspection PyBroadException
        try:
            redis_obj = redis.Redis(connection_pool=self.engine())

            value = redis_obj.get(name)
            return value
        except Exception as error:
            Exception('在 Redis 中获取值时发生问题，详细原因为: {0}'.format(str(error)))
        finally:
            if redis_obj is not None:
                redis_obj.close()

    def delete(self, name):
        """
        返回键name处的值并删除该键，如果键不存在则返回None

        Args:
            name: 键

        Returns:
            值

        """
        redis_obj = None
        # noinspection PyBroadException
        try:
            redis_obj = redis.Redis(connection_pool=self.engine())

            value = redis_obj.delete(name)
            return value
        except Exception as error:
            Exception('在 Redis 中获取值时发生问题，详细原因为: {0}'.format(str(error)))
        finally:
            if redis_obj is not None:
                redis_obj.close()

    def scan(self, cursor=0, match=None, count=None):
        """
        增量返回键名列表。同时返回一个游标表示扫描位置。

        Args:
            cursor: 游标
            match: 允许按模式过滤键
            count: 为Redis提供了关于每批返回的键的数量的提示。

        Returns:
            键名列表

        """
        redis_obj = None
        # noinspection PyBroadException
        try:
            redis_obj = redis.Redis(connection_pool=self.engine())

            keys = redis_obj.scan(cursor=cursor, match=match, count=count)
            return keys
        except Exception as error:
            Exception('在 Redis 中获取键名列表时发生问题，详细原因为: {0}'.format(str(error)))
        finally:
            if redis_obj is not None:
                redis_obj.close()

    def scan_iter(self, match=None, count=None):
        """
        使用SCAN命令创建一个迭代器，这样客户端就不需要记住光标的位置。

        Args:
            match: 允许按模式过滤键
            count: 为Redis提供了关于每批返回的键的数量的提示。

        Returns:
            键名列表迭代器

        """
        redis_obj = None
        # noinspection PyBroadException
        try:
            redis_obj = redis.Redis(connection_pool=self.engine())

            keys_iter = redis_obj.scan_iter(match=match, count=count)
            return keys_iter
        except Exception as error:
            Exception('在 Redis 中获取键名列表迭代器时发生问题，详细原因为: {0}'.format(str(error)))
        finally:
            if redis_obj is not None:
                redis_obj.close()
