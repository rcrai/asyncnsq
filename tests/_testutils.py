import asyncio
import unittest
from functools import wraps


def run_until_complete(fun):
    if not asyncio.iscoroutinefunction(fun):
        fun = asyncio.coroutine(fun)

    @wraps(fun)
    def wrapper(test, *args, **kw):
        print("decorator", test, test.loop, args, kw)
        loop = test.loop
        ret = loop.run_until_complete(fun(test, *args, **kw))
        return ret

    return wrapper


class BaseTest(unittest.TestCase):
    """Base test case for unittests.
    """

    def setUp(self):
        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        pass
        # self.loop.close()
        # del self.loop
