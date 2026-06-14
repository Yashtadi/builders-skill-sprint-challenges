"""
Challenge 5 (Innovate): AWS Study Buddy — MCP-Powered Learning Agent

An interactive agent that searches AWS documentation via MCP, explains concepts
in plain language, and remembers your learning goals and topics across sessions.

Requirements met:
  - Strands Agents SDK
  - AWS Documentation MCP server
  - Amazon Nova Pro (Bedrock)
  - Interactive chat loop
"""

import os
import sys

os.environ["BYPASS_TOOL_CONSENT"] = "true"
os.environ["MEM0_LLM_PROVIDER"] = "litellm"
os.environ["MEM0_LLM_MODEL"] = "bedrock/amazon.nova-micro-v1:0"

from mcp import StdioServerParameters, stdio_client
from strands import Agent
from strands.hooks import BeforeToolCallEvent
from strands.tools.mcp import MCPClient
from strands_tools import mem0_memory

MODEL = "us.amazon.nova-pro-v1:0"
USER_ID = "study_buddy"

aws_docs_mcp = MCPClient(
    lambda: stdio_client(
        StdioServerParameters(command="awslabs.aws-documentation-mcp-server")
    )
)


def stream_handler(**event):
    """Print streamed tokens and MCP tool usage in real time."""
    if "data" in event:
        print(event["data"], end="", flush=True)
    elif "current_tool_use" in event:
        tool_name = event["current_tool_use"].get("name", "")
        if tool_name:
            print(f"\n🔧 Using tool: {tool_name}")


def ensure_memory_user_id(event: BeforeToolCallEvent) -> None:
    """Keep mem0 memories scoped to a single user for reliable recall."""
    if event.tool_use.get("name") == "mem0_memory":
        event.tool_use.setdefault("input", {})["user_id"] = USER_ID


def build_agent(tools):
    agent = Agent(
        model=MODEL,
        tools=tools,
        callback_handler=stream_handler,
        system_prompt=f"""You are AWS Study Buddy — a friendly AWS learning assistant! 📚

You help users learn AWS by searching official documentation and explaining concepts clearly.

AWS Documentation MCP tools (use these to look up facts — never guess):
- search_documentation: find docs for a service or topic
- read_documentation: read a specific documentation page
- read_sections: read specific sections from a page
- recommend: suggest related docs based on what the user is learning

Memory tool (mem0_memory):
- STORE the user's name, AWS experience level, certification goals, and topics they've studied
- RETRIEVE or LIST memories before answering personal or progress questions
- ALWAYS pass user_id="{USER_ID}" on every mem0_memory call

Workflow:
1. When asked about an AWS service, search the docs first, then summarize in plain language
2. After explaining a topic, store what the user learned in memory
3. When the user returns, recall their goals and suggest what to study next
4. Use examples and analogies — keep explanations beginner-friendly unless they say they're advanced

Be encouraging, use emojis sparingly, and cite doc sources when possible.""",
    )
    agent.add_hook(ensure_memory_user_id, BeforeToolCallEvent)
    return agent


def chat_loop(agent):
    print("📚 AWS Study Buddy — MCP + Memory + Streaming")
    print("Ask me anything about AWS! I'll search the official docs and track your progress.")
    print("Examples:")
    print("  • Explain Amazon S3 in simple terms")
    print("  • I'm preparing for Solutions Architect — what should I study first?")
    print("  • What have I studied so far?")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit", "q"}:
            print("Happy studying! Keep building on AWS! 🚀")
            break
        if not user_input:
            continue
        print("Buddy: ", end="")
        agent(user_input)
        print("\n")


def main():
    try:
        with aws_docs_mcp:
            mcp_tools = aws_docs_mcp.list_tools_sync()
            agent = build_agent([*mcp_tools, mem0_memory])
            chat_loop(agent)
    except KeyboardInterrupt:
        print("\nHappy studying! Keep building on AWS! 🚀")
    except Exception as exc:
        print(f"\n❌ Could not start AWS Study Buddy: {exc}", file=sys.stderr)
        print(
            "\nMake sure the MCP server is installed:\n"
            "  pip install awslabs.aws-documentation-mcp-server\n"
            "\nAnd that AWS credentials + Bedrock Nova Pro access are configured.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("\n✅ Challenge 5 complete!")


if __name__ == "__main__":
    main()
