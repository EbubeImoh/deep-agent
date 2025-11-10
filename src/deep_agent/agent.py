"""Utilities for constructing and running the Deep Agent research workflow."""

from __future__ import annotations

import argparse
import getpass
import os
import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, Literal, Optional, Sequence

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient

from deepagents import create_deep_agent

SearchTopic = Literal["general", "news", "finance"]

DEFAULT_SYSTEM_PROMPT = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""


@dataclass
class ResearchAgentConfig:
    """Configuration for building a Deep Agent research assistant."""

    model: str = "gemini-2.5-flash-lite"
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
    prompt_for_google_key: bool = True


load_dotenv()  # load as soon as the module is imported


def _require_env(var_name: str, *, prompt_if_missing: bool = False) -> str:
    """Return env variable or optionally prompt and set it."""
    value = os.getenv(var_name)
    if value:
        return value

    if not prompt_if_missing:
        raise ValueError(f"{var_name} must be set in the environment variables.")

    entered = getpass.getpass(f"Enter value for {var_name}: ").strip()
    if not entered:
        raise ValueError(f"{var_name} is required.")
    os.environ[var_name] = entered
    return entered


def build_internet_search_tool(client: TavilyClient) -> Callable[..., Dict[str, Any]]:
    """Return a callable compatible with deepagents' tool interface."""

    def internet_search(
        query: str,
        max_results: int = 5,
        topic: SearchTopic = "general",
        include_raw_content: bool = False,
    ) -> Dict[str, Any]:
        """Run a Tavily web search."""
        return client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )

    return internet_search


def build_research_agent(config: Optional[ResearchAgentConfig] = None):
    """Create a deep agent instance wired with the Tavily search tool."""
    config = config or ResearchAgentConfig()

    tavily_key = _require_env("TAVILY_API_KEY")
    _require_env("GOOGLE_API_KEY", prompt_if_missing=config.prompt_for_google_key)

    tavily_client = TavilyClient(api_key=tavily_key)
    search_tool = build_internet_search_tool(tavily_client)

    return create_deep_agent(
        tools=[search_tool],
        model=ChatGoogleGenerativeAI(model=config.model),
        system_prompt=config.system_prompt,
    )


def run_research_query(question: str, *, agent=None, config: Optional[ResearchAgentConfig] = None):
    """Invoke the agent with a user question and return the final response content."""
    agent = agent or build_research_agent(config)
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    messages = result.get("messages", [])
    if messages:
        return messages[-1].content
    return result


DEFAULT_CONFIG = ResearchAgentConfig()
agent = build_research_agent(DEFAULT_CONFIG)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Deep Agent research workflow from the CLI.")
    parser.add_argument(
        "question",
        nargs="?",
        help="Research question to send to the agent. If omitted, you will be prompted interactively.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_CONFIG.model,
        help=f"LLM model identifier (default: {DEFAULT_CONFIG.model}).",
    )
    parser.add_argument(
        "--system-prompt",
        help="Optional override for the agent system prompt.",
    )
    parser.add_argument(
        "--no-google-prompt",
        action="store_true",
        help="Fail immediately if GOOGLE_API_KEY is missing instead of prompting via getpass.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Console entry point so `uv run deep-agent <question>` just works."""
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    config = ResearchAgentConfig(
        model=args.model,
        system_prompt=args.system_prompt or DEFAULT_CONFIG.system_prompt,
        prompt_for_google_key=not args.no_google_prompt,
    )

    question = args.question
    while True:
        if not question:
            question = input("Enter research question (type 'quit' to exit): ").strip()
        lowered = question.lower()
        if lowered in {"quit", "exit"}:
            break
        if not question:
            print("Please provide a question or type 'quit' to exit.")
            question = None
            continue

        response = run_research_query(question, config=config)
        print(response)
        print("-" * 40)
        question = None  # force prompt on next loop

    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "ResearchAgentConfig",
    "build_internet_search_tool",
    "build_research_agent",
    "run_research_query",
    "DEFAULT_CONFIG",
    "agent",
    "main",
]
