import asyncio
import sys

from mcp import ClientSession, MCPError
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import INVALID_PARAMS


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

            result = await session.call_tool("fetch", {})
            assert result.is_error
            assert "url" in result.content[0].text

            try:
                await session.get_prompt("fetch", {})
            except MCPError as exc:
                assert exc.error.code == INVALID_PARAMS
            else:
                raise AssertionError("fetch prompt without a URL should raise MCPError")


if __name__ == "__main__":
    asyncio.run(main())
