import asyncio
import sys

from mcp import ClientSession, MCPError
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main() -> None:
    params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server_fetch", "--ignore-robots-txt"],
    )

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            initialized = await session.initialize()
            assert initialized.server_info.name == "mcp-fetch"

            tools = await session.list_tools()
            assert [tool.name for tool in tools.tools] == ["fetch"]

            prompts = await session.list_prompts()
            assert [prompt.name for prompt in prompts.prompts] == ["fetch"]

            for request in (
                session.call_tool("fetch", {}),
                session.get_prompt("fetch", {}),
            ):
                try:
                    await request
                except MCPError as exc:
                    assert exc.code == -32602
                else:
                    raise AssertionError("missing URL should raise MCPError")


if __name__ == "__main__":
    asyncio.run(main())
