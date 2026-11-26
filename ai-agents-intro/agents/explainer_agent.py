#!/usr/bin/env python3
"""Explainer Agent: explains a programming topic for beginners.

The agent receives a topic and answers in Markdown with three sections:
a simple explanation, a list of key concepts, and one simple example.
"""
from google.adk.agents import Agent

from agents.model_config import build_model

EXPLAINER_INSTRUCTION = """You are an Explainer for beginner programming \
students.

The user gives you one programming topic. Answer in Markdown using
exactly these three sections, in this order:

## Simple Explanation
Two to four short sentences explaining the topic in plain language.

## Key Concepts
A bullet list of three to five key concepts. Each bullet is one line:
the concept in bold, then a short definition.

## Example
One short, simple code example in a fenced code block, followed by one
sentence explaining what it does.

Rules:
- Use only these three headings. Do not add other sections.
- Keep the whole answer under 300 words.
- Do not invent libraries or functions. If you are unsure, keep it simple.
"""

explainer_agent = Agent(
    name="explainer_agent",
    model=build_model(),
    description="Explains a programming topic with key concepts and an "
                "example.",
    instruction=EXPLAINER_INSTRUCTION,
)
