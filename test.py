import asyncio
import pytest
from functools import wraps


def connection_context_manager(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        class Wrapper:
            def __init__(self):
                self._conn = None

            async def __aenter__(self):
                self._conn = await func(*args, **kwargs)
                return self._conn

            async def __aexit__(self, *_):
                await self._conn.close()

            def __await__(self):
                return func(
                    *args, **kwargs
                ).__await__()  # https://stackoverflow.com/a/33420721/1113207

        return Wrapper()

    return wrapper


@connection_context_manager
async def connect(uri):
    """
    I don't want to touch this function, other than to
    decorate it with `@connection_context_manager`
    """

    class Connection:
        def __init__(self, uri):
            self.uri = uri
            self.open = True
            print("Connected ", self.uri)

        async def close(self):
            await asyncio.sleep(0.3)
            self.open = False
            print(f"Connection {self.uri} closed")

    await asyncio.sleep(0.3)
    return Connection(uri)


# @wraps(connect)
@pytest.mark.asyncio
async def test_connect_normally():
    connect_is_coroutine = asyncio.iscoroutine(connect)
    no_context = await connect("without context")
    # Now it's open
    assert no_context.open

    await no_context.close()
    # Now it's closed
    assert not no_context.open


@pytest.mark.asyncio
async def test_connect_with_context_manager():
    async with connect("with context uri") as no_context:
        # Now it's open
        assert no_context.open

    # Now it's closed
    assert not no_context.open


if __name__ == "__main__":
    asyncio.run(test_connect())
