import os
from dotenv import load_dotenv
import json
import asyncio
from contextlib import AsyncExitStack
from typing import Optional, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI


load_dotenv()


class IPQueryChat:
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.session: Optional[ClientSession] = None
        self.client = OpenAI(
            base_url='https://api.deepseek.com',
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = 'deepseek-chat'

    async def connect_to_mcp(self) -> None:
        server_params = StdioServerParameters(
            command='uv',
            args=['run', 'ip_query_mcp.py'],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
        await self.session.initialize()

    async def _get_available_tools(self) -> list[Dict[str, Any]]:
        response = await self.session.list_tools()
        return [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
        } for tool in response.tools]

    async def _handle_tool_call(self, content: Any, messages: list) -> str:
        messages.append(content.message.model_dump())

        tool_calls = content.message.tool_calls
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            result = await self.session.call_tool(tool_name, tool_args)
            print(f'调用了 {tool_name} 工具，参数是 {tool_args}')

            messages.append({
                "role": "tool",
                "content": result.content[0].text,
                "tool_call_id": tool_call.id,
            })

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content

    async def chat(self, question: str) -> str:
        if not self.session:
            await self.connect_to_mcp()

        system_prompt = (
            "你是一个有帮助的助手。"
            "如果用户需要查询IP地址信息，请务必调用ip_query工具进行查询，并根据查询结果回答用户。"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=await self._get_available_tools()
        )

        content = response.choices[0]
        if content.finish_reason == "tool_calls":
            return await self._handle_tool_call(content, messages)

        return content.message.content

    async def chat_loop(self) -> None:
        while True:
            try:
                question = input("\nQuery: ").strip()
                if question.lower() in ('q', 'quit'):
                    break
                print("\n" + await self.chat(question))
            except Exception as e:
                print(f"Error: {str(e)}")

    async def close(self) -> None:
        await self.exit_stack.aclose()


async def main() -> None:
    client = IPQueryChat()
    try:
        await client.connect_to_mcp()
        await client.chat_loop()
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
