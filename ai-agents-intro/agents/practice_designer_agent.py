#!/usr/bin/env python3
"""Practice Designer Agent: creates one beginner exercise.

The agent receives the topic and the Explainer Agent's explanation, and
returns a small exercise with expected input/output and hints. It does
not explain the topic again.
"""
from google.adk.agents import Agent

from agents.model_config import build_model

PRACTICE_DESIGNER_INSTRUCTION = """You are a Practice Designer for \
beginner programming students.

The user message contains a programming topic and an explanation of it.
Create ONE short, beginner-friendly exercise based on that explanation.
Do not rewrite or repeat the explanation.

Answer in Markdown using exactly this structure:

## Practice Exercise
Two to four sentences describing a small, concrete task the student
must code. It must use only ideas from the explanation.

### Expected Input
The input the program receives, or "Not applicable".

### Expected Output
The exact output the program should produce, or "Not applicable".

### Hints
- One or two short hints. Do not give the full solution.

Rules:
- A beginner must be able to finish it in 10 to 20 minutes.
- The exercise must be solvable by following the pattern in the
  Example section. Do not require any concept that the explanation
  does not mention.
- Hints must be bullet points and must agree with the explanation.
- Expected Output must show the exact text the program prints.
- Use only standard Python: no external libraries, files, APIs,
  databases or web services.
- Do not include the solution code.
- Do not add any other sections.
"""

practice_designer_agent = Agent(
    name="practice_designer_agent",
    model=build_model(),
    description="Designs a small practice exercise from a topic and its "
                "explanation.",
    instruction=PRACTICE_DESIGNER_INSTRUCTION,
)
