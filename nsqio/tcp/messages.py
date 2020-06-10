from collections import namedtuple
from nsqio.tcp.consts import TOUCH, REQ, FIN


__all__ = ["NsqMessage", "NsqErrorMessage"]


NsqErrorMessage = namedtuple("NsqError", ["code", "msg"])
BaseMessage = namedtuple("NsqMessage", "timestamp attempts message_id body conn")


class NsqMessage(BaseMessage):
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self._is_processed = False
        return self

    @property
    def processed(self):
        """True if message has been processed: finished or re-queued."""
        return self._is_processed

    async def fin(self):
        """Finish a message (indicate successful processing)

        :raises RuntimeWarning: in case message was processed earlier.
        """
        if self._is_processed:
            raise RuntimeWarning("Message has already been processed")
        resp = await self.conn.execute(FIN, self.message_id)
        self._is_processed = True
        return resp

    async def req(self, timeout=10):
        """Re-queue a message (indicate failure to process)

        :param timeout: ``int`` configured max timeout  0 is a special case
            that will not defer re-queueing.
        :raises RuntimeWarning: in case message was processed earlier.
        """
        if self._is_processed:
            raise RuntimeWarning("Message has already been processed")
        resp = await self.conn.execute(REQ, self.message_id, timeout)
        self._is_processed = True
        return resp

    async def touch(self):
        """Reset the timeout for an in-flight message.
        :raises RuntimeWarning: in case message was processed earlier.
        """
        if self._is_processed:
            raise RuntimeWarning("Message has already been processed")
        return await self.conn.execute(TOUCH, self.message_id)
