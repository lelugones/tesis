import asyncio
import threading
import json
from typing import Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    """Synchronous wrapper for MCP client over stdio transport."""

    def __init__(self, command: str, args: list[str], env: dict[str, str] | None = None):
        self.server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env
        )
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        self._exit_stack = None
        self._session = None

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def connect(self):
        """Connect to the stdio server synchronously."""
        future = asyncio.run_coroutine_threadsafe(self._async_connect(), self._loop)
        return future.result()

    async def _async_connect(self):
        self._exit_stack = AsyncExitStack()
        
        stdio_transport = await self._exit_stack.enter_async_context(stdio_client(self.server_params))
        read_stream, write_stream = stdio_transport
        
        self._session = await self._exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
        await self._session.initialize()

    def call_tool(self, name: str, arguments: dict) -> dict | list | str:
        """Call a tool synchronously."""
        if not self._session:
            raise RuntimeError("MCPClient is not connected. Call connect() first.")
        future = asyncio.run_coroutine_threadsafe(self._async_call_tool(name, arguments), self._loop)
        return future.result()

    async def _async_call_tool(self, name: str, arguments: dict) -> Any:
        if self._session is None:
            raise RuntimeError("MCPClient is not connected. Call connect() first.")
        result = await self._session.call_tool(name, arguments=arguments)
        
        if result.content and len(result.content) > 0:
            text_val = getattr(result.content[0], 'text', None)
            if text_val is not None:
                try:
                    return json.loads(text_val)
                except json.JSONDecodeError:
                    return text_val
        return {}

    def disconnect(self):
        """Disconnect synchronously."""
        if not self._session:
            return
        future = asyncio.run_coroutine_threadsafe(self._async_disconnect(), self._loop)
        try:
            future.result(timeout=5.0)
        except Exception:
            pass
        finally:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join(timeout=2.0)
            self._session = None

    async def _async_disconnect(self):
        if self._exit_stack:
            await self._exit_stack.aclose()
