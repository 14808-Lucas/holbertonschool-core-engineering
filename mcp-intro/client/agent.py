#!/usr/bin/env python3
"""Study assistant agent that answers questions through the MCP server."""
import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)
from google.genai import types

load_dotenv()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
MODEL_NAME = os.getenv("MODEL_NAME", "ollama_chat/llama3.2")
OUTPUT_FILE = (Path(__file__).resolve().parent.parent
               / "output" / "sample_agent_response.md")
DEFAULT_QUESTION = ("I want to study Python decorators. "
                    "What should I review first?")

INSTRUCTION = """You are a programming study assistant.

Before answering, always use the MCP tools:
1. Call search_topics with one short keyword from the question,
   for example "decorators".
2. Call get_topic_details with the id of the best matching result.

Answer using only the data returned by the tools. Include:
recommended topic, why it is relevant, prerequisites, key concepts,
one practice idea, and common mistakes to avoid.
Do not invent topic details that the tools did not return.
If no topic matches, say clearly that no matching topic was found.
Keep the answer short and friendly for a student."""


def build_agent(mcp_tools):
    """Create the LLM agent with only the MCP tools it needs."""
    return LlmAgent(
        name="study_assistant",
        model=LiteLlm(model=MODEL_NAME),
        instruction=INSTRUCTION,
        tools=[mcp_tools],
    )


async def ask(question):
    """Send the question to the agent and return (answer, tool_calls)."""
    mcp_tools = McpToolset(
        connection_params=StreamableHTTPConnectionParams(url=MCP_SERVER_URL),
        tool_filter=["search_topics", "get_topic_details"],
    )
    session_service = InMemorySessionService()
    runner = Runner(app_name="mcp_intro", agent=build_agent(mcp_tools),
                    session_service=session_service)
    session = await session_service.create_session(app_name="mcp_intro",
                                                   user_id="student")
    message = types.Content(role="user", parts=[types.Part(text=question)])

    answer = ""
    tool_calls = []
    try:
        available = {tool.name for tool in await mcp_tools.get_tools()}
        missing = {"search_topics", "get_topic_details"} - available
        if missing:
            raise RuntimeError("MCP server is missing tools: {}".format(
                ", ".join(sorted(missing))))
        async for event in runner.run_async(user_id="student",
                                            session_id=session.id,
                                            new_message=message):
            for call in event.get_function_calls():
                tool_calls.append((call.name, dict(call.args or {})))
                print("[MCP call] {}({})".format(
                    call.name, json.dumps(call.args)))
            if event.is_final_response() and event.content:
                answer = "".join(part.text or ""
                                 for part in event.content.parts)
    finally:
        await mcp_tools.close()
    return answer.strip(), tool_calls


def save_response(question, answer, tool_calls):
    """Write the question, MCP tool calls, and answer to the output file."""
    lines = ["# Sample Agent Response", "",
             "**Question:** {}".format(question), "",
             "**Model:** `{}`  ".format(MODEL_NAME),
             "**MCP server:** `{}`".format(MCP_SERVER_URL), "",
             "## MCP Tool Calls", ""]
    for number, (name, args) in enumerate(tool_calls, 1):
        lines.append("{}. `{}({})`".format(number, name, json.dumps(args)))
    lines += ["", "## Answer", "", answer, ""]
    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")


def main():
    """Read the question, run the agent, and save the response."""
    question = " ".join(sys.argv[1:]) or DEFAULT_QUESTION
    print("Question: {}".format(question))
    try:
        answer, tool_calls = asyncio.run(ask(question))
    except Exception as error:
        print("Error: could not run the agent: {}".format(error),
              file=sys.stderr)
        print("Check that the MCP server is running at {} and that "
              "Ollama is running.".format(MCP_SERVER_URL), file=sys.stderr)
        return 1

    called = [name for name, _ in tool_calls]
    if "search_topics" not in called:
        print("Error: the agent answered without calling search_topics "
              "through MCP. Response not saved. Try running again.",
              file=sys.stderr)
        return 1
    if "get_topic_details" not in called:
        print("Note: get_topic_details was not called "
              "(expected only when no topic matches).")

    print("\nAnswer:\n{}".format(answer))
    save_response(question, answer, tool_calls)
    print("\nSaved to {}".format(OUTPUT_FILE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
